"""
Response utilities for optimizing API responses
"""
from typing import Any, Dict, List, Optional
import json

def slim_response(data: Any, fields: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> Any:
    """
    Slim down response data by including/excluding fields
    
    Args:
        data: Response data to slim
        fields: List of fields to include (if specified, only these fields are included)
        exclude: List of fields to exclude
    
    Returns:
        Slimmed response data
    """
    if isinstance(data, dict):
        result = {}
        
        if fields:
            # Include only specified fields
            for field in fields:
                if field in data:
                    result[field] = slim_response(data[field], fields=None, exclude=exclude)
        else:
            # Include all fields except excluded ones
            for key, value in data.items():
                if exclude and key in exclude:
                    continue
                result[key] = slim_response(value, fields=None, exclude=exclude)
        
        return result
    
    elif isinstance(data, list):
        return [slim_response(item, fields=fields, exclude=exclude) for item in data]
    
    else:
        return data

def paginate_response(
    items: List[Any],
    page: int = 1,
    per_page: int = 20,
    total: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a paginated response
    
    Args:
        items: List of items to paginate
        page: Current page number (1-indexed)
        per_page: Items per page
        total: Total number of items (if known)
    
    Returns:
        Paginated response dictionary
    """
    if total is None:
        total = len(items)
    
    total_pages = (total + per_page - 1) // per_page
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
    }

def compress_json(data: Any, remove_nulls: bool = True, remove_empty: bool = False) -> Any:
    """
    Compress JSON data by removing null values and empty collections
    
    Args:
        data: Data to compress
        remove_nulls: Remove null/None values
        remove_empty: Remove empty lists/dicts
    
    Returns:
        Compressed data
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            compressed_value = compress_json(value, remove_nulls, remove_empty)
            
            # Skip null values if requested
            if remove_nulls and compressed_value is None:
                continue
            
            # Skip empty collections if requested
            if remove_empty:
                if isinstance(compressed_value, (list, dict)) and not compressed_value:
                    continue
            
            result[key] = compressed_value
        
        return result
    
    elif isinstance(data, list):
        return [compress_json(item, remove_nulls, remove_empty) for item in data]
    
    else:
        return data

def format_datetime_fields(data: Any, fields: List[str], format: str = "%Y-%m-%d %H:%M:%S") -> Any:
    """
    Format datetime fields in response data
    
    Args:
        data: Response data
        fields: List of datetime field names to format
        format: DateTime format string
    
    Returns:
        Data with formatted datetime fields
    """
    if isinstance(data, dict):
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                if hasattr(result[field], 'strftime'):
                    result[field] = result[field].strftime(format)
        
        # Recursively format nested data
        for key, value in result.items():
            if isinstance(value, (dict, list)):
                result[key] = format_datetime_fields(value, fields, format)
        
        return result
    
    elif isinstance(data, list):
        return [format_datetime_fields(item, fields, format) for item in data]
    
    else:
        return data