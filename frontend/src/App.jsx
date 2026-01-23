import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import ImageUpload from './components/ImageUpload'
import DetectionResults from './components/DetectionResults'
import CostEstimation from './components/CostEstimation'
import LoadingSpinner from './components/LoadingSpinner'
import { detectDamage, createEstimation } from './services/api'

function App() {
  // State management
  const [uploadedImage, setUploadedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [detectionData, setDetectionData] = useState(null)
  const [costEstimation, setCostEstimation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [step, setStep] = useState(1) // 1: Upload, 2: Detection, 3: Cost

  // Handle image upload
  const handleImageUpload = (file) => {
    setUploadedImage(file)
    setImagePreview(URL.createObjectURL(file))
    setDetectionData(null)
    setCostEstimation(null)
    setError(null)
    setStep(1)
  }

  // Handle damage detection
  const handleDetect = async () => {
    if (!uploadedImage) return

    setLoading(true)
    setError(null)

    try {
      const result = await detectDamage(uploadedImage)
      setDetectionData(result)
      setStep(2)
      
      // Show success message if no damages found
      if (result.total_damages === 0) {
        setError({
          type: 'info',
          message: 'No damages detected! Your car looks great! 🎉'
        })
      }
    } catch (err) {
      setError({
        type: 'error',
        message: err.message || 'Failed to detect damages. Please try again.'
      })
    } finally {
      setLoading(false)
    }
  }

  // Handle cost estimation
  const handleEstimate = async () => {
    if (!detectionData || detectionData.total_damages === 0) return

    setLoading(true)
    setError(null)

    try {
      const result = await createEstimation(detectionData.detection_id)
      setCostEstimation(result)
      setStep(3)
    } catch (err) {
      setError({
        type: 'error',
        message: err.message || 'Failed to estimate costs. Please try again.'
      })
    } finally {
      setLoading(false)
    }
  }

  // Reset everything
  const handleReset = () => {
    setUploadedImage(null)
    setImagePreview(null)
    setDetectionData(null)
    setCostEstimation(null)
    setError(null)
    setStep(1)
  }

  return (
    <div className="min-h-screen pb-20">
      {/* Animated background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-center gap-4">
            {/* Step 1: Upload */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className={`flex items-center gap-2 ${step >= 1 ? 'opacity-100' : 'opacity-40'}`}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                step >= 1 ? 'gradient-bg text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                1
              </div>
              <span className="font-semibold">Upload</span>
            </motion.div>

            <div className="w-16 h-1 bg-gray-300 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: step >= 2 ? '100%' : '0%' }}
                className="h-full gradient-bg"
                transition={{ duration: 0.5 }}
              />
            </div>

            {/* Step 2: Detect */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className={`flex items-center gap-2 ${step >= 2 ? 'opacity-100' : 'opacity-40'}`}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                step >= 2 ? 'gradient-bg text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                2
              </div>
              <span className="font-semibold">Detect</span>
            </motion.div>

            <div className="w-16 h-1 bg-gray-300 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: step >= 3 ? '100%' : '0%' }}
                className="h-full gradient-bg"
                transition={{ duration: 0.5 }}
              />
            </div>

            {/* Step 3: Estimate */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4 }}
              className={`flex items-center gap-2 ${step >= 3 ? 'opacity-100' : 'opacity-40'}`}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                step >= 3 ? 'gradient-bg text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                3
              </div>
              <span className="font-semibold">Cost</span>
            </motion.div>
          </div>
        </div>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`mb-6 p-4 rounded-xl glass-effect ${
                error.type === 'error' ? 'border-l-4 border-danger-500' : 'border-l-4 border-primary-500'
              }`}
            >
              <p className={`font-semibold ${
                error.type === 'error' ? 'text-danger-700' : 'text-primary-700'
              }`}>
                {error.message}
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading Spinner */}
        {loading && <LoadingSpinner />}

        {/* Content based on step */}
        <AnimatePresence mode="wait">
          {!uploadedImage ? (
            // Step 1: Upload Image
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <ImageUpload onImageUpload={handleImageUpload} />
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            >
              {/* Left Column: Image and Detection Results */}
              <div className="space-y-6">
                {/* Uploaded Image Preview */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="glass-effect rounded-2xl overflow-hidden"
                >
                  <img
                    src={imagePreview}
                    alt="Uploaded car"
                    className="w-full h-auto"
                  />
                </motion.div>

                {/* Action Buttons */}
                <div className="flex gap-4">
                  <button
                    onClick={handleReset}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-xl transition-all duration-200"
                  >
                    Upload New Image
                  </button>
                  
                  {!detectionData && (
                    <button
                      onClick={handleDetect}
                      disabled={loading}
                      className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Detect Damage
                    </button>
                  )}
                </div>
              </div>

              {/* Right Column: Results */}
              <div className="space-y-6">
                {/* Detection Results */}
                {detectionData && (
                  <DetectionResults
                    data={detectionData}
                    onEstimate={handleEstimate}
                    hasEstimation={!!costEstimation}
                    loading={loading}
                  />
                )}

                {/* Cost Estimation */}
                {costEstimation && (
                  <CostEstimation data={costEstimation} />
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App