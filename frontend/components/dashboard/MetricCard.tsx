import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  icon: LucideIcon;
  title: string;
  value: string | number;
  unit?: string;
  color?: 'blue' | 'green' | 'orange' | 'purple' | 'red' | 'yellow';
  trend?: {
    value: number;
    isPositive: boolean;
  };
  description?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  icon: Icon,
  title,
  value,
  unit = '',
  color = 'blue',
  trend,
  description
}) => {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      border: 'border-blue-200'
    },
    green: {
      bg: 'bg-green-50',
      text: 'text-green-600',
      border: 'border-green-200'
    },
    orange: {
      bg: 'bg-orange-50',
      text: 'text-orange-600',
      border: 'border-orange-200'
    },
    purple: {
      bg: 'bg-purple-50',
      text: 'text-purple-600',
      border: 'border-purple-200'
    },
    red: {
      bg: 'bg-red-50',
      text: 'text-red-600',
      border: 'border-red-200'
    },
    yellow: {
      bg: 'bg-yellow-50',
      text: 'text-yellow-600',
      border: 'border-yellow-200'
    }
  };

  const colors = colorClasses[color];

  return (
    <div className={`bg-white p-6 rounded-lg shadow-sm border ${colors.border} hover:shadow-md transition-shadow`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className={`p-3 rounded-lg ${colors.bg}`}>
            <Icon size={24} className={colors.text} />
          </div>
          <div>
            <p className="text-sm text-gray-600 font-medium">{title}</p>
            <div className="flex items-baseline space-x-1">
              <p className="text-2xl font-bold text-gray-900">{value}</p>
              {unit && <span className="text-lg text-gray-600">{unit}</span>}
            </div>
            {description && (
              <p className="text-xs text-gray-500 mt-1">{description}</p>
            )}
          </div>
        </div>
        
        {trend && (
          <div className={`flex items-center text-sm ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
            <span>{trend.isPositive ? '↑' : '↓'}</span>
            <span className="ml-1">{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;