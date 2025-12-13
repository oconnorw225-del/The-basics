/**
 * Appen Provider
 * Integrates with Appen for crowd-sourced data annotation and AI training
 */

const tasks = new Map();
let enabled = false;

const stats = {
  tasksSubmitted: 0,
  tasksCompleted: 0,
  tasksFailed: 0,
  qualityScore: 0
};

/**
 * Initialize the provider
 */
async function initialize() {
  console.log('Initializing Appen provider...');
  // Enable if Appen credentials are configured
  enabled = !!process.env.APPEN_API_KEY;
  if (!enabled) {
    console.log('  ⚠️  Appen disabled (APPEN_API_KEY not set)');
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
 * Submit a task to Appen
 */
async function submitTask(task, priority = 'normal') {
  if (!enabled) {
    throw new Error('Appen provider not enabled');
  }

  const taskId = `appen_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  const taskData = {
    id: taskId,
    ...task,
    priority,
    status: 'submitted',
    submittedAt: Date.now(),
    provider: 'appen'
  };

  tasks.set(taskId, taskData);
  stats.tasksSubmitted++;

  // In production, submit job to Appen API
  // const job = await appen.createJob({ ... });

  return { taskId, status: 'submitted' };
}

/**
 * Poll for completed tasks from Appen
 */
async function pollTasks() {
  if (!enabled) return [];

  // In production, poll Appen for completed jobs
  // const completedJobs = await appen.listCompletedJobs({ ... });
  
  return [];
}

/**
 * Submit result (quality check and finalize)
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

  // Update quality score
  if (stats.tasksCompleted > 0) {
    stats.qualityScore = (stats.tasksCompleted / (stats.tasksCompleted + stats.tasksFailed)) * 100;
  }

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
