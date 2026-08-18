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

export const CashBurnChart = ({ trajectoryPoints = [] }) => {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={trajectoryPoints} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
          <XAxis dataKey="month" stroke="#64748B" fontSize={11} tickLine={false} />
          <YAxis stroke="#64748B" fontSize={11} tickLine={false} unit="M" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0F172A',
              borderColor: '#334155',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            formatter={(value) => [`$${value}M`, '']}
          />
          <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
          <Line
            type="monotone"
            dataKey="baseline_cash_m"
            name="Baseline (CY)"
            stroke="#0284C7"
            strokeWidth={2.5}
            dot={{ r: 3, fill: '#0284C7' }}
          />
          <Line
            type="monotone"
            dataKey="simulated_cash_m"
            name="Simulated Scenario"
            stroke="#10B981"
            strokeWidth={2.5}
            strokeDasharray="3 3"
            dot={{ r: 3, fill: '#10B981' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
