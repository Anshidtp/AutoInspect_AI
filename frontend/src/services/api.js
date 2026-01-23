import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api/v1', // Proxied through Vite to http://localhost:8000/api/v1
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error occurred'
      throw new Error(message)
    } else if (error.request) {
      // Request was made but no response
      throw new Error('Cannot connect to server. Please ensure the backend is running.')
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred')
    }
  }
)

/**
 * Upload image and detect damages
 * @param {File} imageFile - Image file to upload
 * @param {number} confidenceThreshold - Optional confidence threshold (0-1)
 * @returns {Promise} Detection results
 */
export const detectDamage = async (imageFile, confidenceThreshold = 0.25) => {
  try {
    // Create form data
    const formData = new FormData()
    formData.append('file', imageFile)
    formData.append('confidence_threshold', confidenceThreshold)
    formData.append('detect_severity', true)

    // Make request
    const response = await api.post('/detections/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  } catch (error) {
    console.error('Detection error:', error)
    throw error
  }
}

/**
 * Create cost estimation for detected damages
 * @param {number} detectionId - Detection record ID
 * @param {Object} options - Optional estimation parameters
 * @returns {Promise} Cost estimation results
 */
export const createEstimation = async (detectionId, options = {}) => {
  try {
    const payload = {
      detection_id: detectionId,
      include_paint: options.includePaint !== false,
      labor_rate_override: options.laborRate || null,
      markup_override: options.markup || null,
    }

    const response = await api.post('/estimations/', payload)
    return response.data
  } catch (error) {
    console.error('Estimation error:', error)
    throw error
  }
}

/**
 * Get detection by ID
 * @param {number} detectionId - Detection record ID
 * @returns {Promise} Detection details
 */
export const getDetection = async (detectionId) => {
  try {
    const response = await api.get(`/detections/${detectionId}`)
    return response.data
  } catch (error) {
    console.error('Get detection error:', error)
    throw error
  }
}

/**
 * Get cost estimation by detection ID
 * @param {number} detectionId - Detection record ID
 * @returns {Promise} Cost estimation details
 */
export const getEstimation = async (detectionId) => {
  try {
    const response = await api.get(`/estimations/detection/${detectionId}`)
    return response.data
  } catch (error) {
    console.error('Get estimation error:', error)
    throw error
  }
}

/**
 * Get estimation summary
 * @param {number} detectionId - Detection record ID
 * @returns {Promise} Estimation summary
 */
export const getEstimationSummary = async (detectionId) => {
  try {
    const response = await api.get(`/estimations/summary/${detectionId}`)
    return response.data
  } catch (error) {
    console.error('Get summary error:', error)
    throw error
  }
}

/**
 * List all detections with pagination
 * @param {number} page - Page number
 * @param {number} pageSize - Items per page
 * @returns {Promise} Paginated detection list
 */
export const listDetections = async (page = 1, pageSize = 10) => {
  try {
    const response = await api.get('/detections/', {
      params: { page, page_size: pageSize }
    })
    return response.data
  } catch (error) {
    console.error('List detections error:', error)
    throw error
  }
}

/**
 * Check API health
 * @returns {Promise} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await axios.get('http://localhost:8000/health')
    return response.data
  } catch (error) {
    console.error('Health check error:', error)
    throw error
  }
}

export default api