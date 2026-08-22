import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

const defaultData = [
  { month: 'Jan', cashBalance: 12.45, cashBurnBaseline: 11.2 },
  { month: 'Feb', cashBalance: 12.1, cashBurnBaseline: 10.8 },
  { month: 'Mar', cashBalance: 11.8, cashBurnBaseline: 10.4 },
  { month: 'Apr', cashBalance: 11.4, cashBurnBaseline: 10.0 },
  { month: 'May', cashBalance: 11.0, cashBurnBaseline: 9.6 },
  { month: 'Jun', cashBalance: 10.6, cashBurnBaseline: 9.2 },
  { month: 'Jul', cashBalance: 10.2, cashBurnBaseline: 8.8 },
  { month: 'Aug', cashBalance: 9.8, cashBurnBaseline: 8.4 },
  { month: 'Sep', cashBalance: 9.4, cashBurnBaseline: 8.0 },
  { month: 'Oct', cashBalance: 9.0, cashBurnBaseline: 7.6 },
  { month: 'Nov', cashBalance: 8.7, cashBurnBaseline: 7.2 },
  { month: 'Dec', cashBalance: 8.4, cashBurnBaseline: 6.8 },
];

export const LiquidityTrendChart = ({ data = defaultData }) => {
  return (
    <div className="w-full h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
          <XAxis dataKey="month" stroke="#64748B" fontSize={10} tickLine={false} />
          <YAxis stroke="#64748B" fontSize={10} tickLine={false} unit="M" />
          <Tooltip
            contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
            itemStyle={{ color: '#F8FAFC' }}
          />
          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
          <Line
            type="monotone"
            dataKey="cashBalance"
            name="Cash Balance (Actual)"
            stroke="#0284C7"
            strokeWidth={2}
            dot={{ r: 3, fill: '#0284C7' }}
          />
          <Line
            type="monotone"
            dataKey="cashBurnBaseline"
            name="Cash Burn (Baseline)"
            stroke="#10B981"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={{ r: 2, fill: '#10B981' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
