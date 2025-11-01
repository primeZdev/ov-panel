import { useState, useEffect, useMemo } from 'react';
import apiClient from '../services/api';
import { FiCpu, FiHardDrive, FiClock, FiServer, FiCheckCircle, FiXCircle, FiUsers } from 'react-icons/fi';
import { BsDeviceSsd } from "react-icons/bs";
import { useTranslation } from 'react-i18next';

const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

const formatUptime = (seconds) => {
  const d = Math.floor(seconds / (3600 * 24));
  const h = Math.floor(seconds % (3600 * 24) / 3600);
  return `${d}d ${h}h`;
};

const StatCard = ({ icon, label, value, subValue, className, color }) => {
  return (
    <div className={`stat-card ${className}`}>
       <div className="icon-background" style={{ backgroundColor: color ? `${color}20` : 'var(--accent-color-transparent)' }}>
        {icon}
      </div>
      <div className="stat-card-content">
        <span>{label}</span>
        <h3 style={{ color }}>{value}</h3>
        {subValue && <p>{subValue}</p>}
      </div>
    </div>
  );
};

const ServerStats = () => {
  const [stats, setStats] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [users, setUsers] = useState([]);
  const { t } = useTranslation();

  const nodeStats = useMemo(() => {
    const activeCount = nodes.filter((node) => node.status).length;
    return {
      total: nodes.length,
      active: activeCount,
      inactive: nodes.length - activeCount,
    };
  }, [nodes]);

  const userStats = useMemo(() => {
    const activeUsers = users.filter(user => user.is_active).length;
    const inactiveUsers = users.length - activeUsers;
    return {
      total: users.length,
      active: activeUsers,
      inactive: inactiveUsers,
    };
  }, [users]);

  useEffect(() => {
    const fetchServerData = async () => {
      try {
        
        const response = await apiClient.get('/settings/server/info');
        if (response.data.success) {
          setStats(response.data.data);
        }
      } catch (error) {
        console.error("Error fetching server info:", error);
      }
    };

    const fetchNodes = async () => {
      try {
        const response = await apiClient.get('/node/list');
        if (response.data.success) {
          setNodes(response.data.data || []);
        }
      } catch (error) {
        console.error("Error fetching nodes:", error);
      }
    };

    const fetchUsers = async () => {
      try {
        const response = await apiClient.get('/user/all');
        if (response.data.success) {
          setUsers(response.data.data || []);
        }
      } catch (error) {
        console.error("Error fetching users:", error);
      }
    };

    fetchServerData();
    fetchNodes();
    fetchUsers();
    const intervalId = setInterval(fetchServerData, 5000);

    return () => clearInterval(intervalId);
  }, []);

  if (!stats) {
    return <div>Loading server information...</div>;
  }

  return (
    <div id="dashboard-view" className="view">
      <div className="view-header">
        <h2>{t('dashboard')}</h2>
      </div>

      <h3 className="section-title">{t('server')}</h3>
      <div className="stats-grid">
        <StatCard
          icon={<FiCpu className="icon" />}
          label={t('averageCPU')}
          value={`${stats.cpu.toFixed(1)}%`}
          subValue={t('currentUsage')}
          className="card-orange"
          color="var(--accent-color)"
        />
        <StatCard
          icon={<BsDeviceSsd className="icon" />}
          label={t('memory')}
          value={`${stats.memory_percent.toFixed(1)}%`}
          subValue={`${formatBytes(stats.memory_used)} / ${formatBytes(stats.memory_total)}`}
          className="card-green"
          color="var(--success-color)"
        />
        <StatCard
          icon={<FiHardDrive className="icon" />}
          label={t('disk')}
          value={`${stats.disk_percent.toFixed(1)}%`}
          subValue={`${formatBytes(stats.disk_used)} / ${formatBytes(stats.disk_total)}`}
          className="card-blue"
          color="var(--info-color)"
        />
        <StatCard
          icon={<FiClock className="icon" />}
          label={t('uptime')}
          value={formatUptime(stats.uptime)}
          subValue={t('sinceLastBoot')}
          className="card-blue"
          color="var(--info-color)"
        />
      </div>

      <h3 className="section-title">{t('nodes')}</h3>
      <div className="stats-grid">
        <StatCard
          icon={<FiServer className="icon" />}
          label={t('nodesTotal')}
          value={nodeStats.total}
          className="card-orange"
          color="var(--accent-color)"
        />
        <StatCard
          icon={<FiCheckCircle className="icon" />}
          label={t('nodesActive')}
          value={nodeStats.active}
          className="card-green"
          color="var(--success-color)"
        />
        <StatCard
          icon={<FiXCircle className="icon" />}
          label={t('nodesInactive')}
          value={nodeStats.inactive}
          className="card-red"
          color="var(--danger-color)"
        />
      </div>

      <h3 className="section-title">{t('users')}</h3>
      <div className="stats-grid">
        <StatCard
          icon={<FiUsers className="icon" />}
          label={t('totalUsers')}
          value={userStats.total}
          className="card-orange"
          color="var(--accent-color)"
        />
        <StatCard
          icon={<FiCheckCircle className="icon" />}
          label={t('activeUsers')}
          value={userStats.active}
          className="card-green"
          color="var(--success-color)"
        />
        <StatCard
          icon={<FiXCircle className="icon" />}
          label={t('inactiveUsers')}
          value={userStats.inactive}
          className="card-red"
          color="var(--danger-color)"
        />
      </div>
    </div>
  );
};

export default ServerStats;