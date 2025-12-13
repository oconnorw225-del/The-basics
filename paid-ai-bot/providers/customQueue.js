/**
 * Custom Queue Provider
 * Internal task queue system for direct task management
 */

// In-memory task storage (use database in production)
const tasks = new Map();
const taskQueue = [];
let taskIdCounter = 1;

let enabled = true;
const stats = {
  tasksSubmitted: 0,
  tasksCompleted: 0,
  tasksFailed: 0,
  tasksInQueue: 0
};

/**
 * Initialize the provider
 */
async function initialize() {
  console.log('Initializing Custom Queue provider...');
  enabled = true;
  return true;
}

/**
 * Check if provider is enabled
 */
function isEnabled() {
  return enabled;
}

/**
 * Submit a task to the queue
 */
async function submitTask(task, priority = 'normal') {
  const taskId = `custom_${taskIdCounter++}`;
  
  const taskData = {
    id: taskId,
    ...task,
    priority,
    status: 'queued',
    submittedAt: Date.now(),
    provider: 'customQueue'
  };

  tasks.set(taskId, taskData);
  
  // Insert based on priority
  if (priority === 'urgent') {
    taskQueue.unshift(taskData);
  } else if (priority === 'high') {
    // Insert after urgent tasks
    const urgentIndex = taskQueue.findIndex(t => t.priority !== 'urgent');
    if (urgentIndex === -1) {
      taskQueue.push(taskData);
    } else {
      taskQueue.splice(urgentIndex, 0, taskData);
    }
  } else {
    taskQueue.push(taskData);
  }

  stats.tasksSubmitted++;
  stats.tasksInQueue = taskQueue.length;

  return {
    taskId,
    status: 'queued',
    position: taskQueue.findIndex(t => t.id === taskId) + 1
  };
}

/**
 * Poll for new tasks (for internal processing)
 */
async function pollTasks() {
  // Return tasks that are ready to process
  const readyTasks = taskQueue.filter(t => t.status === 'queued').slice(0, 5);
  
  // Mark as processing
  readyTasks.forEach(task => {
    task.status = 'processing';
    task.startedAt = Date.now();
  });

  return readyTasks;
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

  // Remove from queue
  const queueIndex = taskQueue.findIndex(t => t.id === taskId);
  if (queueIndex !== -1) {
    taskQueue.splice(queueIndex, 1);
  }

  if (result.success) {
    stats.tasksCompleted++;
  } else {
    stats.tasksFailed++;
  }
  stats.tasksInQueue = taskQueue.length;

  return task;
}

/**
 * Get task status
 */
async function getTaskStatus(taskId) {
  const task = tasks.get(taskId);
  
  if (!task) {
    return null;
  }

  return {
    id: task.id,
    status: task.status,
    priority: task.priority,
    submittedAt: task.submittedAt,
    startedAt: task.startedAt,
    completedAt: task.completedAt,
    result: task.result
  };
}

/**
 * Get provider statistics
 */
function getStats() {
  return {
    ...stats,
    averageProcessingTime: calculateAverageProcessingTime()
  };
}

/**
 * Calculate average processing time
 */
function calculateAverageProcessingTime() {
  const completedTasks = Array.from(tasks.values()).filter(
    t => t.status === 'completed' && t.startedAt && t.completedAt
  );

  if (completedTasks.length === 0) return 0;

  const totalTime = completedTasks.reduce(
    (sum, task) => sum + (task.completedAt - task.startedAt),
    0
  );

  return totalTime / completedTasks.length;
}

/**
 * Get all tasks
 */
function getAllTasks() {
  return Array.from(tasks.values());
}

/**
 * Clear completed tasks (cleanup)
 */
function clearCompletedTasks(olderThanMs = 3600000) {
  const now = Date.now();
  let cleared = 0;

  for (const [id, task] of tasks.entries()) {
    if (
      (task.status === 'completed' || task.status === 'failed') &&
      task.completedAt &&
      now - task.completedAt > olderThanMs
    ) {
      tasks.delete(id);
      cleared++;
    }
  }

  return cleared;
}

module.exports = {
  initialize,
  isEnabled,
  submitTask,
  pollTasks,
  submitResult,
  getTaskStatus,
  getStats,
  getAllTasks,
  clearCompletedTasks
};
