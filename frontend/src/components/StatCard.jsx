import React from "react";

const StatCard = ({ icon, label, value, sub, accent, trend }) => (
  <div className="stat-card" style={{ "--accent": accent }}>
    <div className="stat-card-top">
      <span className="stat-icon">{icon}</span>
      {trend !== undefined && (
        <span className={`stat-trend ${trend >= 0 ? "up" : "down"}`}>
          {trend >= 0 ? "▲" : "▼"} {Math.abs(trend)}%
        </span>
      )}
    </div>
    <div className="stat-value">{value}</div>
    <div className="stat-label">{label}</div>
    {sub && <div className="stat-sub">{sub}</div>}
    <div className="stat-bar">
      <div className="stat-bar-fill" />
    </div>
  </div>
);

export default StatCard;
