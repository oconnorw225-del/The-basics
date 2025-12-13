/**
 * Feature Manager System
 * Centralized registry and lifecycle management for all features
 */

import { EventEmitter } from 'events';

class FeatureManager extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = config;
    this.features = new Map();
    this.featureInstances = new Map();
    this.featureStatus = new Map();
    this.dependencies = new Map();
    this.startOrder = [];
    
    this.state = {
      initialized: false,
      starting: false,
      running: false
    };
  }

  /**
   * Register a feature with its constructor and configuration
   */
  registerFeature(name, FeatureClass, options = {}) {
    if (this.features.has(name)) {
      console.warn(`⚠️ Feature ${name} already registered, overwriting...`);
    }

    const featureConfig = {
      name,
      FeatureClass,
      enabled: options.enabled ?? true,
      critical: options.critical ?? false,
      dependencies: options.dependencies || [],
      config: options.config || {},
      autoStart: options.autoStart ?? true
    };

    this.features.set(name, featureConfig);
    this.dependencies.set(name, featureConfig.dependencies);
    
    this.featureStatus.set(name, {
      enabled: featureConfig.enabled,
      initialized: false,
      running: false,
      healthy: true,
      error: null,
      startedAt: null,
      metrics: {}
    });

    console.log(`📦 Registered feature: ${name}${featureConfig.critical ? ' (CRITICAL)' : ''}`);
    this.emit('featureRegistered', { name, config: featureConfig });

    return this;
  }

  /**
   * Get all registered features
   */
  getAllFeatures() {
    const features = {};
    
    this.features.forEach((config, name) => {
      features[name] = {
        ...config,
        status: this.featureStatus.get(name)
      };
    });

    return features;
  }

  /**
   * Get feature status
   */
  getFeatureStatus(name) {
    return this.featureStatus.get(name) || null;
  }

  /**
   * Enable a feature
   */
  async enableFeature(name) {
    const feature = this.features.get(name);
    
    if (!feature) {
      throw new Error(`Feature ${name} not found`);
    }

    const status = this.featureStatus.get(name);
    status.enabled = true;

    console.log(`✅ Feature ${name} enabled`);
    this.emit('featureEnabled', { name });

    // Auto-start if system is running
    if (this.state.running && feature.autoStart) {
      await this.startFeature(name);
    }

    return status;
  }

  /**
   * Disable a feature
   */
  async disableFeature(name) {
    const status = this.featureStatus.get(name);
    
    if (!status) {
      throw new Error(`Feature ${name} not found`);
    }

    // Stop if running
    if (status.running) {
      await this.stopFeature(name);
    }

    status.enabled = false;
    console.log(`⏸️ Feature ${name} disabled`);
    this.emit('featureDisabled', { name });

    return status;
  }

  /**
   * Resolve dependency order for feature initialization
   */
  resolveDependencyOrder() {
    const visited = new Set();
    const order = [];
    const visiting = new Set();

    const visit = (name) => {
      if (visited.has(name)) {
        return;
      }

      if (visiting.has(name)) {
        throw new Error(`Circular dependency detected involving ${name}`);
      }

      visiting.add(name);
      
      const deps = this.dependencies.get(name) || [];
      for (const dep of deps) {
        if (!this.features.has(dep)) {
          throw new Error(`Missing dependency: ${name} requires ${dep}`);
        }
        visit(dep);
      }

      visiting.delete(name);
      visited.add(name);
      order.push(name);
    };

    // Visit all features
    this.features.forEach((_, name) => {
      visit(name);
    });

    this.startOrder = order;
    return order;
  }

  /**
   * Initialize all enabled features in dependency order
   */
  async initializeAll() {
    if (this.state.initialized) {
      console.log('⚠️ Features already initialized');
      return;
    }

    console.log('🚀 Initializing features...');

    // Resolve dependency order
    try {
      this.resolveDependencyOrder();
      console.log(`📋 Feature initialization order: ${this.startOrder.join(' → ')}`);
    } catch (error) {
      console.error('❌ Failed to resolve dependencies:', error.message);
      throw error;
    }

    // Initialize features in order
    for (const name of this.startOrder) {
      const feature = this.features.get(name);
      const status = this.featureStatus.get(name);

      if (!status.enabled) {
        console.log(`⏭️ Skipping disabled feature: ${name}`);
        continue;
      }

      try {
        await this.initializeFeature(name);
      } catch (error) {
        console.error(`❌ Failed to initialize ${name}:`, error.message);
        
        if (feature.critical) {
          throw new Error(`Critical feature ${name} failed to initialize: ${error.message}`);
        }
        
        status.error = error.message;
        status.healthy = false;
      }
    }

    this.state.initialized = true;
    this.emit('allInitialized');
    console.log('✅ All features initialized');
  }

  /**
   * Initialize a single feature
   */
  async initializeFeature(name) {
    const feature = this.features.get(name);
    const status = this.featureStatus.get(name);

    if (!feature) {
      throw new Error(`Feature ${name} not found`);
    }

    if (status.initialized) {
      console.log(`⚠️ Feature ${name} already initialized`);
      return;
    }

    console.log(`🔧 Initializing ${name}...`);

    try {
      // Create instance
      const instance = new feature.FeatureClass(feature.config);
      this.featureInstances.set(name, instance);

      // Call initialize if available
      if (typeof instance.initialize === 'function') {
        await instance.initialize();
      }

      status.initialized = true;
      status.healthy = true;
      status.error = null;

      console.log(`✅ ${name} initialized`);
      this.emit('featureInitialized', { name });
      
      return instance;
    } catch (error) {
      status.error = error.message;
      status.healthy = false;
      throw error;
    }
  }

  /**
   * Start all enabled features in dependency order
   */
  async startAll() {
    if (this.state.running) {
      console.log('⚠️ Features already running');
      return;
    }

    if (!this.state.initialized) {
      await this.initializeAll();
    }

    console.log('🚀 Starting features...');
    this.state.starting = true;

    for (const name of this.startOrder) {
      const feature = this.features.get(name);
      const status = this.featureStatus.get(name);

      if (!status.enabled || !status.initialized) {
        continue;
      }

      if (!feature.autoStart) {
        console.log(`⏭️ Skipping non-autostart feature: ${name}`);
        continue;
      }

      try {
        await this.startFeature(name);
      } catch (error) {
        console.error(`❌ Failed to start ${name}:`, error.message);
        
        if (feature.critical) {
          this.state.starting = false;
          throw new Error(`Critical feature ${name} failed to start: ${error.message}`);
        }
      }
    }

    this.state.starting = false;
    this.state.running = true;
    this.emit('allStarted');
    console.log('✅ All features started');
  }

  /**
   * Start a single feature
   */
  async startFeature(name) {
    const instance = this.featureInstances.get(name);
    const status = this.featureStatus.get(name);

    if (!instance) {
      throw new Error(`Feature ${name} not initialized`);
    }

    if (status.running) {
      console.log(`⚠️ Feature ${name} already running`);
      return;
    }

    console.log(`▶️ Starting ${name}...`);

    try {
      // Call start if available
      if (typeof instance.start === 'function') {
        await instance.start();
      }

      status.running = true;
      status.healthy = true;
      status.error = null;
      status.startedAt = new Date().toISOString();

      console.log(`✅ ${name} started`);
      this.emit('featureStarted', { name });
      
      return instance;
    } catch (error) {
      status.error = error.message;
      status.healthy = false;
      throw error;
    }
  }

  /**
   * Stop a single feature
   */
  async stopFeature(name) {
    const instance = this.featureInstances.get(name);
    const status = this.featureStatus.get(name);

    if (!instance) {
      console.warn(`⚠️ Feature ${name} not found`);
      return;
    }

    if (!status.running) {
      console.log(`⚠️ Feature ${name} not running`);
      return;
    }

    console.log(`⏸️ Stopping ${name}...`);

    try {
      // Call stop if available
      if (typeof instance.stop === 'function') {
        await instance.stop();
      }

      status.running = false;
      status.startedAt = null;

      console.log(`✅ ${name} stopped`);
      this.emit('featureStopped', { name });
    } catch (error) {
      console.error(`❌ Error stopping ${name}:`, error.message);
      status.error = error.message;
      throw error;
    }
  }

  /**
   * Stop all features in reverse order
   */
  async stopAll() {
    if (!this.state.running) {
      console.log('⚠️ Features not running');
      return;
    }

    console.log('🛑 Stopping all features...');

    // Stop in reverse order
    const reverseOrder = [...this.startOrder].reverse();

    for (const name of reverseOrder) {
      const status = this.featureStatus.get(name);

      if (status.running) {
        try {
          await this.stopFeature(name);
        } catch (error) {
          console.error(`❌ Error stopping ${name}:`, error.message);
        }
      }
    }

    this.state.running = false;
    this.emit('allStopped');
    console.log('✅ All features stopped');
  }

  /**
   * Get feature instance
   */
  getFeature(name) {
    return this.featureInstances.get(name);
  }

  /**
   * Update feature health status
   */
  updateFeatureHealth(name, healthy, metrics = {}) {
    const status = this.featureStatus.get(name);
    
    if (!status) {
      return;
    }

    const wasHealthy = status.healthy;
    status.healthy = healthy;
    status.metrics = { ...status.metrics, ...metrics };

    if (wasHealthy && !healthy) {
      console.warn(`⚠️ Feature ${name} became unhealthy`);
      this.emit('featureUnhealthy', { name, metrics });
    } else if (!wasHealthy && healthy) {
      console.log(`✅ Feature ${name} recovered`);
      this.emit('featureRecovered', { name, metrics });
    }
  }

  /**
   * Get system health overview
   */
  getSystemHealth() {
    const health = {
      healthy: true,
      features: {},
      summary: {
        total: this.features.size,
        enabled: 0,
        running: 0,
        healthy: 0,
        unhealthy: 0
      }
    };

    this.featureStatus.forEach((status, name) => {
      health.features[name] = { ...status };

      if (status.enabled) health.summary.enabled++;
      if (status.running) health.summary.running++;
      if (status.healthy) health.summary.healthy++;
      else health.summary.unhealthy++;

      const feature = this.features.get(name);
      if (feature.critical && !status.healthy) {
        health.healthy = false;
      }
    });

    return health;
  }

  /**
   * Graceful shutdown
   */
  async shutdown() {
    console.log('🛑 FeatureManager shutting down...');
    
    await this.stopAll();
    
    this.featureInstances.clear();
    this.removeAllListeners();
    
    this.state.initialized = false;
    this.state.running = false;
    
    console.log('✅ FeatureManager shut down');
  }
}

export default FeatureManager;
