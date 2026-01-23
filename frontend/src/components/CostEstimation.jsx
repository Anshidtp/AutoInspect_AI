import { motion } from 'framer-motion'
import { DollarSign, Wrench, Paintbrush, Package, TrendingUp, Download } from 'lucide-react'

const CostEstimation = ({ data }) => {
  const {
    parts_cost,
    labor_cost,
    paint_cost,
    markup,
    total_cost,
    estimated_labor_hours,
    labor_rate,
    markup_percentage,
    damage_items
  } = data

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  // Download report
  const downloadReport = () => {
    const reportContent = `
CAR DAMAGE REPAIR COST ESTIMATION
==================================

Total Cost: ${formatCurrency(total_cost)}

Cost Breakdown:
- Parts: ${formatCurrency(parts_cost)}
- Labor: ${formatCurrency(labor_cost)} (${estimated_labor_hours}hrs @ ${formatCurrency(labor_rate)}/hr)
- Paint: ${formatCurrency(paint_cost)}
- Markup (${markup_percentage}%): ${formatCurrency(markup)}

Itemized Damages:
${damage_items.map((item, i) => `
${i + 1}. ${item.damage_type.replace(/_/g, ' ')} (${item.severity})
   - Parts: ${formatCurrency(item.parts_cost)}
   - Labor: ${formatCurrency(item.labor_cost)} (${item.labor_hours}hrs)
   - Paint: ${formatCurrency(item.paint_cost)}
   - Subtotal: ${formatCurrency(item.subtotal)}
`).join('\n')}

Generated: ${new Date().toLocaleString()}
    `.trim()

    const blob = new Blob([reportContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `damage-report-${Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-effect rounded-2xl overflow-hidden"
    >
      {/* Header with Total */}
      <div className="gradient-bg p-6 text-white">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-2xl font-bold">Cost Estimation</h3>
          <button
            onClick={downloadReport}
            className="bg-white/20 hover:bg-white/30 p-2 rounded-lg transition-colors"
            title="Download Report"
          >
            <Download className="w-5 h-5" />
          </button>
        </div>
        <div className="text-center py-6">
          <p className="text-white/80 text-sm mb-2">Total Repair Cost</p>
          <motion.p
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200 }}
            className="text-5xl font-bold"
          >
            {formatCurrency(total_cost)}
          </motion.p>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="p-6 space-y-4">
        <h4 className="font-semibold text-gray-700 mb-4">Cost Breakdown</h4>

        {/* Parts */}
        <CostRow
          icon={<Package className="w-5 h-5 text-blue-500" />}
          label="Parts"
          amount={parts_cost}
          color="blue"
        />

        {/* Labor */}
        <CostRow
          icon={<Wrench className="w-5 h-5 text-orange-500" />}
          label={`Labor (${estimated_labor_hours}hrs @ ${formatCurrency(labor_rate)}/hr)`}
          amount={labor_cost}
          color="orange"
        />

        {/* Paint */}
        <CostRow
          icon={<Paintbrush className="w-5 h-5 text-purple-500" />}
          label="Paint & Finish"
          amount={paint_cost}
          color="purple"
        />

        {/* Markup */}
        <CostRow
          icon={<TrendingUp className="w-5 h-5 text-green-500" />}
          label={`Markup (${markup_percentage}%)`}
          amount={markup}
          color="green"
        />

        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-gray-800">Total</span>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
              {formatCurrency(total_cost)}
            </span>
          </div>
        </div>
      </div>

      {/* Itemized Damages */}
      <div className="p-6 bg-gray-50 space-y-3">
        <h4 className="font-semibold text-gray-700 mb-4">Itemized Damages</h4>
        
        <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
          {damage_items.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-lg p-4 border border-gray-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h5 className="font-semibold text-gray-800 capitalize">
                    {item.damage_type.replace(/_/g, ' ').replace(/-/g, ' ')}
                  </h5>
                  <span className={`badge ${
                    item.severity === 'severe' ? 'badge-danger' :
                    item.severity === 'moderate' ? 'badge-warning' :
                    'badge-success'
                  } text-xs mt-1`}>
                    {item.severity}
                  </span>
                </div>
                <span className="text-lg font-bold text-primary-600">
                  {formatCurrency(item.subtotal)}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2 text-xs text-gray-600">
                <div>
                  <p className="text-gray-400">Parts</p>
                  <p className="font-semibold">{formatCurrency(item.parts_cost)}</p>
                </div>
                <div>
                  <p className="text-gray-400">Labor</p>
                  <p className="font-semibold">{formatCurrency(item.labor_cost)}</p>
                </div>
                <div>
                  <p className="text-gray-400">Paint</p>
                  <p className="font-semibold">{formatCurrency(item.paint_cost)}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="p-4 bg-yellow-50 border-t border-yellow-200">
        <p className="text-xs text-yellow-800 text-center">
          ℹ️ This is an automated estimate. Actual costs may vary based on location, parts availability, and shop rates.
        </p>
      </div>
    </motion.div>
  )
}

const CostRow = ({ icon, label, amount, color }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value)
  }

  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg bg-${color}-100 flex items-center justify-center`}>
          {icon}
        </div>
        <span className="text-gray-700">{label}</span>
      </div>
      <span className="font-semibold text-gray-800">{formatCurrency(amount)}</span>
    </div>
  )
}

export default CostEstimation