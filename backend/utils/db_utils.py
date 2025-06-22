"""
Database optimization utilities
"""
from typing import List, Type, Optional, Any
from sqlalchemy.orm import Query, load_only, joinedload, selectinload, Session
from sqlalchemy import and_, or_, func
import logging

logger = logging.getLogger(__name__)

def optimize_query(
    query: Query,
    load_fields: Optional[List[str]] = None,
    eager_load: Optional[List[str]] = None,
    select_in_load: Optional[List[str]] = None
) -> Query:
    """
    Optimize database query with selective field loading and eager loading
    
    Args:
        query: SQLAlchemy query object
        load_fields: Fields to load (reduces data transfer)
        eager_load: Relationships to eager load (reduces N+1 queries)
        select_in_load: Relationships to load with selectinload (better for one-to-many)
    
    Returns:
        Optimized query
    """
    if load_fields:
        query = query.options(load_only(*load_fields))
    
    if eager_load:
        for relation in eager_load:
            query = query.options(joinedload(relation))
    
    if select_in_load:
        for relation in select_in_load:
            query = query.options(selectinload(relation))
    
    return query

def batch_query(
    db: Session,
    model: Type[Any],
    ids: List[Any],
    batch_size: int = 100
) -> List[Any]:
    """
    Query database in batches to avoid memory issues
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        ids: List of IDs to query
        batch_size: Size of each batch
    
    Returns:
        List of results
    """
    results = []
    
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i + batch_size]
        batch_results = db.query(model).filter(
            model.id.in_(batch_ids)
        ).all()
        results.extend(batch_results)
    
    return results

def get_query_count(query: Query) -> int:
    """
    Get count of query results efficiently
    
    Args:
        query: SQLAlchemy query
    
    Returns:
        Count of results
    """
    count_query = query.statement.with_only_columns([func.count()]).order_by(None)
    count = query.session.execute(count_query).scalar()
    return count

def prefetch_related(
    objects: List[Any],
    relation_name: str,
    db: Session,
    filter_func: Optional[callable] = None
) -> None:
    """
    Manually prefetch related objects to avoid N+1 queries
    
    Args:
        objects: List of objects to prefetch relations for
        relation_name: Name of the relation to prefetch
        db: Database session
        filter_func: Optional function to filter related objects
    """
    if not objects:
        return
    
    # Get the relationship property
    model_class = type(objects[0])
    relation_property = getattr(model_class, relation_name).property
    
    # Get the related model class
    related_model = relation_property.mapper.class_
    
    # Get the foreign key column
    foreign_key_col = list(relation_property.local_columns)[0]
    
    # Extract IDs
    ids = [getattr(obj, foreign_key_col.name) for obj in objects]
    ids = list(set(filter(None, ids)))  # Remove duplicates and None values
    
    if not ids:
        return
    
    # Query related objects
    related_query = db.query(related_model).filter(
        related_model.id.in_(ids)
    )
    
    if filter_func:
        related_query = filter_func(related_query)
    
    related_objects = related_query.all()
    
    # Create lookup dictionary
    related_dict = {obj.id: obj for obj in related_objects}
    
    # Assign to original objects
    for obj in objects:
        related_id = getattr(obj, foreign_key_col.name)
        if related_id in related_dict:
            setattr(obj, relation_name, related_dict[related_id])

def bulk_insert_or_update(
    db: Session,
    model: Type[Any],
    data: List[dict],
    unique_fields: List[str],
    batch_size: int = 1000
) -> int:
    """
    Bulk insert or update records
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        data: List of dictionaries with data
        unique_fields: Fields that determine uniqueness
        batch_size: Size of each batch
    
    Returns:
        Number of records processed
    """
    if not data:
        return 0
    
    processed = 0
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        
        # Build unique constraint query
        for record in batch:
            filters = [
                getattr(model, field) == record[field]
                for field in unique_fields
            ]
            
            existing = db.query(model).filter(and_(*filters)).first()
            
            if existing:
                # Update existing record
                for key, value in record.items():
                    setattr(existing, key, value)
            else:
                # Insert new record
                new_record = model(**record)
                db.add(new_record)
            
            processed += 1
        
        # Commit batch
        try:
            db.commit()
        except Exception as e:
            logger.error(f"Bulk insert/update error: {e}")
            db.rollback()
            raise
    
    return processed

def optimize_pagination(
    query: Query,
    page: int,
    per_page: int,
    max_per_page: int = 100
) -> tuple[List[Any], int]:
    """
    Optimize pagination with efficient counting
    
    Args:
        query: SQLAlchemy query
        page: Page number (1-indexed)
        per_page: Items per page
        max_per_page: Maximum items per page
    
    Returns:
        Tuple of (items, total_count)
    """
    # Limit per_page to max
    per_page = min(per_page, max_per_page)
    
    # Get total count efficiently
    total_count = get_query_count(query)
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get items
    items = query.offset(offset).limit(per_page).all()
    
    return items, total_count