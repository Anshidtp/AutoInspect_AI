import { motion } from 'framer-motion'
import { Car, Sparkles } from 'lucide-react'

const Header = () => {
  return (
    <header className="glass-effect border-b border-white/20 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3"
          >
            <div className="w-12 h-12 gradient-bg rounded-xl flex items-center justify-center shadow-lg">
              <Car className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                AutoInspect AI
              </h1>
              <p className="text-sm text-gray-600">Powered by Scipy Technologies</p>
            </div>
          </motion.div>

          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="hidden md:flex items-center gap-2 bg-gradient-to-r from-success-50 to-primary-50 px-4 py-2 rounded-full border border-success-200"
          >
            <Sparkles className="w-4 h-4 text-success-600" />
            <span className="text-sm font-semibold text-success-700">AI-Powered Analysis</span>
          </motion.div>
        </div>
      </div>
    </header>
  )
}

export default Header