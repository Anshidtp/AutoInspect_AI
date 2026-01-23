import { motion } from 'framer-motion'
import { AlertCircle, CheckCircle, DollarSign, Clock } from 'lucide-react'

const DetectionResults = ({ data, onEstimate, hasEstimation, loading }) => {
  const { damages_detected, total_damages, processing_time } = data

  // Get severity badge color
  const getSeverityBadge = (severity) => {
    const badges = {
      minor: 'badge-success',
      moderate: 'badge-warning',
      severe: 'badge-danger'
    }
    return badges[severity] || 'badge-warning'
  }

  // Get severity icon
  const getSeverityIcon = (severity) => {
    if (severity === 'severe') return '🔴'
    if (severity === 'moderate') return '🟡'
    return '🟢'
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass-effect rounded-2xl p-6 space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 pb-4">
        <h3 className="text-2xl font-bold text-gray-800">Detection Results</h3>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Clock className="w-4 h-4" />
          <span>{processing_time?.toFixed(2)}s</span>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-4 border border-primary-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary-500 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-primary-600 font-medium">Total Damages</p>
              <p className="text-3xl font-bold text-primary-700">{total_damages}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-success-50 to-success-100 rounded-xl p-4 border border-success-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-success-500 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-success-600 font-medium">Confidence</p>
              <p className="text-3xl font-bold text-success-700">
                {damages_detected.length > 0
                  ? `${(damages_detected.reduce((acc, d) => acc + d.confidence, 0) / damages_detected.length * 100).toFixed(0)}%`
                  : 'N/A'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Damages List */}
      {damages_detected.length > 0 ? (
        <div className="space-y-3">
          <h4 className="font-semibold text-gray-700 text-lg">Detected Damages</h4>
          
          <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
            {damages_detected.map((damage, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{getSeverityIcon(damage.severity)}</span>
                    <div>
                      <h5 className="font-semibold text-gray-800 capitalize">
                        {damage.damage_type.replace(/_/g, ' ').replace(/-/g, ' ')}
                      </h5>
                      <p className="text-sm text-gray-500">
                        {damage.affected_part && `Affected: ${damage.affected_part}`}
                      </p>
                    </div>
                  </div>
                  <span className={`badge ${getSeverityBadge(damage.severity)}`}>
                    {damage.severity}
                  </span>
                </div>

                {/* Confidence Bar */}
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                    <span>Confidence</span>
                    <span className="font-semibold">{(damage.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${damage.confidence * 100}%` }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                      className={`h-full rounded-full ${
                        damage.confidence > 0.7 ? 'bg-success-500' :
                        damage.confidence > 0.4 ? 'bg-warning-500' :
                        'bg-danger-500'
                      }`}
                    />
                  </div>
                </div>

                {/* Location Info */}
                <div className="mt-2 text-xs text-gray-500">
                  Location: {(damage.bbox_x * 100).toFixed(0)}%, {(damage.bbox_y * 100).toFixed(0)}%
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-success-100 rounded-full mx-auto mb-4 flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-success-600" />
          </div>
          <p className="text-lg font-semibold text-gray-700">No damages detected!</p>
          <p className="text-gray-500">Your car looks great! 🎉</p>
        </div>
      )}

      {/* Get Cost Estimation Button */}
      {!hasEstimation && total_damages > 0 && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={onEstimate}
          disabled={loading}
          className="w-full btn-secondary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <DollarSign className="w-5 h-5" />
          Get Cost Estimation
        </motion.button>
      )}
    </motion.div>
  )
}

export default DetectionResults