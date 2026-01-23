import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, Image as ImageIcon, Camera } from 'lucide-react'

const ImageUpload = ({ onImageUpload }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onImageUpload(acceptedFiles[0])
    }
  }, [onImageUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1,
    multiple: false
  })

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-3xl mx-auto"
    >
      {/* Upload Card */}
      <div className="glass-effect rounded-2xl p-8 md:p-12">
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
            className="w-20 h-20 gradient-bg rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-2xl"
          >
            <Camera className="w-10 h-10 text-white" />
          </motion.div>
          
          <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
            Upload Car Image
          </h2>
          <p className="text-gray-600 text-lg">
            Get instant AI-powered damage analysis and cost estimation
          </p>
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`
            border-3 border-dashed rounded-2xl p-12 cursor-pointer
            transition-all duration-300 ease-in-out
            ${isDragActive 
              ? 'border-primary-500 bg-primary-50 scale-105' 
              : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            }
          `}
        >
          <input {...getInputProps()} />
          
          <div className="text-center">
            <motion.div
              animate={{
                y: isDragActive ? -10 : 0,
              }}
              className="mb-6"
            >
              {isDragActive ? (
                <Upload className="w-16 h-16 mx-auto text-primary-500 animate-bounce" />
              ) : (
                <ImageIcon className="w-16 h-16 mx-auto text-gray-400" />
              )}
            </motion.div>

            <div className="space-y-2">
              <p className="text-xl font-semibold text-gray-700">
                {isDragActive ? 'Drop your image here' : 'Drag & drop your car image'}
              </p>
              <p className="text-gray-500">
                or click to browse
              </p>
            </div>

            <div className="mt-6 flex items-center justify-center gap-2">
              <span className="badge bg-blue-100 text-blue-700 border-blue-300">JPG</span>
              <span className="badge bg-purple-100 text-purple-700 border-purple-300">JPEG</span>
              <span className="badge bg-pink-100 text-pink-700 border-pink-300">PNG</span>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <FeatureCard
            icon="🎯"
            title="Accurate Detection"
            description="AI identifies all visible damages"
          />
          <FeatureCard
            icon="⚡"
            title="Instant Analysis"
            description="Results in seconds"
          />
          <FeatureCard
            icon="💰"
            title="Cost Estimation"
            description="Get repair cost breakdown"
          />
        </div>
      </div>
    </motion.div>
  )
}

const FeatureCard = ({ icon, title, description }) => (
  <motion.div
    whileHover={{ scale: 1.05 }}
    className="text-center p-4 rounded-xl bg-gradient-to-br from-white to-gray-50 border border-gray-200"
  >
    <div className="text-3xl mb-2">{icon}</div>
    <h3 className="font-semibold text-gray-800 mb-1">{title}</h3>
    <p className="text-sm text-gray-600">{description}</p>
  </motion.div>
)

export default ImageUpload