/**
 * Direct Clients Provider
 * Manages tasks from direct client relationships
 */

const tasks = new Map();
let enabled = false;

const stats = {
  tasksSubmitted: 0,
  tasksCompleted: 0,
  tasksFailed: 0,
  activeClients: 0
};

/**
 * Initialize the provider
 */
async function initialize() {
  console.log('Initializing Direct Clients provider...');
  // Enable if API credentials are configured
  enabled = !!process.env.DIRECT_CLIENT_API_KEY;
  if (!enabled) {
    console.log('  ⚠️  Direct Clients disabled (DIRECT_CLIENT_API_KEY not set)');
  }
  return enabled;
}

/**
 * Check if provider is enabled
 */
function isEnabled() {
  return enabled;
}

/**
 * Submit a task
 */
async function submitTask(task, priority = 'normal') {
  if (!enabled) {
    throw new Error('Direct Clients provider not enabled');
  }

  const taskId = `direct_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  const taskData = {
    id: taskId,
    ...task,
    priority,
    status: 'submitted',
    submittedAt: Date.now(),
    provider: 'directClients'
  };

  tasks.set(taskId, taskData);
  stats.tasksSubmitted++;

  return { taskId, status: 'submitted' };
}

/**
 * Poll for new tasks from direct clients
 */
async function pollTasks() {
  if (!enabled) return [];

  // In production, this would poll an external API or webhook
  // For now, return empty array
  return [];
}

/**
 * Submit result for a task
 */
async function submitResult(taskId, result) {
  const task = tasks.get(taskId);
  
  if (!task) {
    throw new Error(`Task ${taskId} not found`);
  }

  task.status = result.success ? 'completed' : 'failed';
  task.completedAt = Date.now();
  task.result = result;

  if (result.success) {
    stats.tasksCompleted++;
  } else {
    stats.tasksFailed++;
  }

  // In production, send result back to client API
  return task;
}

/**
 * Get task status
 */
async function getTaskStatus(taskId) {
  return tasks.get(taskId) || null;
}

/**
 * Get provider statistics
 */
function getStats() {
  return { ...stats };
}

module.exports = {
  initialize,
  isEnabled,
  submitTask,
  pollTasks,
  submitResult,
  getTaskStatus,
  getStats
};
