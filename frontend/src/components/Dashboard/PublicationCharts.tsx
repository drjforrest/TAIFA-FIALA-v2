'use client'

import { usePublicationStats } from '@/hooks/usePublications'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

export default function PublicationCharts() {
  const { bySource, byYear, byDomain, totalPublications, avgAfricanScore, avgAiScore, loading, error } = usePublicationStats()

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-gray-200 dark:bg-gray-700 rounded-lg h-80"></div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-600 dark:text-red-400">Failed to load publication charts: {error}</p>
      </div>
    )
  }

  // Chart configurations
  const sourceData = {
    labels: Object.keys(bySource),
    datasets: [
      {
        label: 'Publications by Source',
        data: Object.values(bySource),
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)', // blue
          'rgba(16, 185, 129, 0.8)', // green
          'rgba(245, 101, 101, 0.8)', // red
          'rgba(251, 191, 36, 0.8)', // yellow
          'rgba(139, 92, 246, 0.8)', // purple
        ],
        borderColor: [
          'rgba(59, 130, 246, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(245, 101, 101, 1)',
          'rgba(251, 191, 36, 1)',
          'rgba(139, 92, 246, 1)',
        ],
        borderWidth: 2,
      },
    ],
  }

  const yearData = {
    labels: Object.keys(byYear).sort(),
    datasets: [
      {
        label: 'Publications by Year',
        data: Object.keys(byYear).sort().map(year => byYear[year]),
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  }

  const domainData = {
    labels: Object.keys(byDomain).slice(0, 8), // Top 8 domains
    datasets: [
      {
        label: 'Publications by Domain',
        data: Object.keys(byDomain).slice(0, 8).map(domain => byDomain[domain]),
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(245, 101, 101, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(236, 72, 153, 0.8)',
          'rgba(20, 184, 166, 0.8)',
          'rgba(161, 161, 170, 0.8)',
        ],
        borderWidth: 0,
      },
    ],
  }

  const relevanceData = {
    labels: ['African Relevance', 'AI Technology Relevance'],
    datasets: [
      {
        label: 'Average Relevance Scores',
        data: [avgAfricanScore * 100, avgAiScore * 100],
        backgroundColor: [
          'rgba(245, 101, 101, 0.8)',
          'rgba(59, 130, 246, 0.8)',
        ],
        borderColor: [
          'rgba(245, 101, 101, 1)',
          'rgba(59, 130, 246, 1)',
        ],
        borderWidth: 2,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: 'rgb(107, 114, 128)', // gray-500
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: 'rgb(107, 114, 128)',
        },
        grid: {
          color: 'rgba(107, 114, 128, 0.1)',
        },
      },
      y: {
        ticks: {
          color: 'rgb(107, 114, 128)',
        },
        grid: {
          color: 'rgba(107, 114, 128, 0.1)',
        },
      },
    },
  }

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: 'rgb(107, 114, 128)',
        },
      },
    },
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Publication Analytics
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Analysis of {totalPublications.toLocaleString()} research publications in the African AI ecosystem
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Publications by Source */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Publications by Source
          </h4>
          <div className="h-64">
            <Doughnut data={sourceData} options={doughnutOptions} />
          </div>
        </div>

        {/* Publications by Year */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Publications Over Time
          </h4>
          <div className="h-64">
            <Line data={yearData} options={chartOptions} />
          </div>
        </div>

        {/* Publications by Domain */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Research Domains
          </h4>
          <div className="h-64">
            <Bar data={domainData} options={chartOptions} />
          </div>
        </div>

        {/* Relevance Scores */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Average Relevance Scores
          </h4>
          <div className="h-64">
            <Doughnut data={relevanceData} options={doughnutOptions} />
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-white">
          <h5 className="text-sm font-medium opacity-90 mb-1">Most Active Source</h5>
          <p className="text-xl font-bold">
            {Object.keys(bySource).sort((a, b) => bySource[b] - bySource[a])[0] || 'N/A'}
          </p>
          <p className="text-sm opacity-75">
            {Math.max(...Object.values(bySource))} publications
          </p>
        </div>

        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-4 text-white">
          <h5 className="text-sm font-medium opacity-90 mb-1">Top Research Domain</h5>
          <p className="text-xl font-bold">
            {Object.keys(byDomain).sort((a, b) => byDomain[b] - byDomain[a])[0] || 'N/A'}
          </p>
          <p className="text-sm opacity-75">
            {Math.max(...Object.values(byDomain))} publications
          </p>
        </div>

        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-4 text-white">
          <h5 className="text-sm font-medium opacity-90 mb-1">Peak Publication Year</h5>
          <p className="text-xl font-bold">
            {Object.keys(byYear).sort((a, b) => byYear[b] - byYear[a])[0] || 'N/A'}
          </p>
          <p className="text-sm opacity-75">
            {Math.max(...Object.values(byYear))} publications
          </p>
        </div>
      </div>
    </div>
  )
}