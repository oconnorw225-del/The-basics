/**
 * Process Linker System
 * Links all components with service discovery and dependency resolution
 */

import { EventEmitter } from 'events';

class ProcessLinker extends EventEmitter {
  constructor() {
    super();
    
    this.services = new Map();
    this.connections = new Map();
    this.eventBus = new EventEmitter();
    this.sharedState = new Map();
    
    this.state = {
      initialized: false,
      linked: false
    };

    // Set higher limit for event listeners
    this.eventBus.setMaxListeners(100);
  }

  /**
   * Register a service
   */
  registerService(name, service, metadata = {}) {
    if (this.services.has(name)) {
      console.warn(`⚠️ Service ${name} already registered, overwriting...`);
    }

    this.services.set(name, {
      name,
      service,
      metadata: {
        type: metadata.type || 'generic',
        provides: metadata.provides || [],
        requires: metadata.requires || [],
        ...metadata
      },
      registeredAt: new Date().toISOString()
    });

    console.log(`🔗 Registered service: ${name}`);
    this.emit('serviceRegistered', { name, metadata });
    
    return this;
  }

  /**
   * Unregister a service
   */
  unregisterService(name) {
    if (!this.services.has(name)) {
      console.warn(`⚠️ Service ${name} not found`);
      return;
    }

    // Remove all connections involving this service
    const connectionsToRemove = [];
    this.connections.forEach((conn, key) => {
      if (conn.from === name || conn.to === name) {
        connectionsToRemove.push(key);
      }
    });

    connectionsToRemove.forEach(key => this.connections.delete(key));

    this.services.delete(name);
    console.log(`🔌 Unregistered service: ${name}`);
    this.emit('serviceUnregistered', { name });
  }

  /**
   * Discover a service by name
   */
  discover(name) {
    const serviceInfo = this.services.get(name);
    return serviceInfo ? serviceInfo.service : null;
  }

  /**
   * Discover services by type or capability
   */
  discoverByType(type) {
    const matches = [];
    
    this.services.forEach((info, name) => {
      if (info.metadata.type === type) {
        matches.push({ name, service: info.service });
      }
    });

    return matches;
  }

  /**
   * Discover services that provide a specific capability
   */
  discoverByCapability(capability) {
    const matches = [];
    
    this.services.forEach((info, name) => {
      if (info.metadata.provides && info.metadata.provides.includes(capability)) {
        matches.push({ name, service: info.service });
      }
    });

    return matches;
  }

  /**
   * Link all registered services
   */
  async link(features = {}) {
    if (this.state.linked) {
      console.log('⚠️ Services already linked');
      return;
    }

    console.log('🔗 Linking all services...');

    // Auto-register features as services
    Object.entries(features).forEach(([name, feature]) => {
      if (feature.status && feature.status.initialized) {
        this.registerService(name, feature, {
          type: 'feature',
          critical: feature.critical
        });
      }
    });

    // Resolve dependencies
    const dependencies = this.resolveDependencies();
    console.log(`📋 Dependency map:`, dependencies);

    // Establish connections
    await this.establishConnections(dependencies);

    // Setup event forwarding
    this.setupEventBus();

    this.state.linked = true;
    this.emit('linked');
    console.log('✅ All services linked');
  }

  /**
   * Resolve service dependencies
   */
  resolveDependencies() {
    const dependencies = {};

    this.services.forEach((info, name) => {
      const requires = info.metadata.requires || [];
      dependencies[name] = [];

      requires.forEach(requirement => {
        // Find services that provide this requirement
        const providers = this.discoverByCapability(requirement);
        
        if (providers.length === 0) {
          console.warn(`⚠️ No provider found for ${requirement} required by ${name}`);
        } else {
          dependencies[name].push(...providers.map(p => p.name));
        }
      });
    });

    return dependencies;
  }

  /**
   * Establish connections between services
   */
  async establishConnections(dependencies) {
    for (const [serviceName, deps] of Object.entries(dependencies)) {
      for (const depName of deps) {
        await this.connect(serviceName, depName);
      }
    }
  }

  /**
   * Connect two services
   */
  async connect(fromName, toName) {
    const from = this.services.get(fromName);
    const to = this.services.get(toName);

    if (!from || !to) {
      console.warn(`⚠️ Cannot connect ${fromName} to ${toName}: service not found`);
      return;
    }

    const connectionKey = `${fromName}→${toName}`;
    
    if (this.connections.has(connectionKey)) {
      console.log(`⚠️ Connection ${connectionKey} already exists`);
      return;
    }

    this.connections.set(connectionKey, {
      from: fromName,
      to: toName,
      establishedAt: new Date().toISOString()
    });

    console.log(`🔗 Connected: ${connectionKey}`);
    this.emit('connected', { from: fromName, to: toName });

    // If services have onConnect handler, call it
    if (typeof from.service.onConnect === 'function') {
      await from.service.onConnect(toName, to.service);
    }
  }

  /**
   * Disconnect two services
   */
  async disconnect(fromName, toName) {
    const connectionKey = `${fromName}→${toName}`;
    
    if (!this.connections.has(connectionKey)) {
      console.warn(`⚠️ Connection ${connectionKey} does not exist`);
      return;
    }

    const from = this.services.get(fromName);
    
    // If service has onDisconnect handler, call it
    if (from && typeof from.service.onDisconnect === 'function') {
      await from.service.onDisconnect(toName);
    }

    this.connections.delete(connectionKey);
    console.log(`🔌 Disconnected: ${connectionKey}`);
    this.emit('disconnected', { from: fromName, to: toName });
  }

  /**
   * Setup centralized event bus
   */
  setupEventBus() {
    console.log('📡 Setting up event bus...');

    // Allow services to subscribe to events
    this.services.forEach((info, name) => {
      const service = info.service;

      // If service has event subscriptions, set them up
      if (service.eventSubscriptions) {
        Object.entries(service.eventSubscriptions).forEach(([eventName, handler]) => {
          this.eventBus.on(eventName, handler.bind(service));
          console.log(`📡 ${name} subscribed to event: ${eventName}`);
        });
      }
    });

    console.log('✅ Event bus configured');
  }

  /**
   * Publish event to event bus
   */
  publish(eventName, data) {
    this.eventBus.emit(eventName, {
      event: eventName,
      data,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Subscribe to event on event bus
   */
  subscribe(eventName, handler) {
    this.eventBus.on(eventName, handler);
  }

  /**
   * Get or set shared state
   */
  getSharedState(key) {
    return this.sharedState.get(key);
  }

  setSharedState(key, value) {
    const oldValue = this.sharedState.get(key);
    this.sharedState.set(key, value);
    
    this.publish('stateChanged', { key, oldValue, newValue: value });
    
    return value;
  }

  /**
   * Get all services
   */
  getAllServices() {
    const services = {};
    
    this.services.forEach((info, name) => {
      services[name] = {
        name: info.name,
        type: info.metadata.type,
        metadata: info.metadata,
        registeredAt: info.registeredAt
      };
    });

    return services;
  }

  /**
   * Get all connections
   */
  getAllConnections() {
    const connections = [];
    
    this.connections.forEach((conn, key) => {
      connections.push({
        key,
        from: conn.from,
        to: conn.to,
        establishedAt: conn.establishedAt
      });
    });

    return connections;
  }

  /**
   * Get service graph for visualization
   */
  getServiceGraph() {
    const nodes = [];
    const edges = [];

    this.services.forEach((info, name) => {
      nodes.push({
        id: name,
        type: info.metadata.type,
        provides: info.metadata.provides,
        requires: info.metadata.requires
      });
    });

    this.connections.forEach((conn) => {
      edges.push({
        from: conn.from,
        to: conn.to
      });
    });

    return { nodes, edges };
  }

  /**
   * Coordinate startup of all services
   */
  async coordinateStartup(services) {
    console.log('🚀 Coordinating service startup...');

    for (const [name, service] of Object.entries(services)) {
      if (typeof service.start === 'function') {
        try {
          console.log(`▶️ Starting ${name}...`);
          await service.start();
          this.publish('serviceStarted', { name });
        } catch (error) {
          console.error(`❌ Failed to start ${name}:`, error.message);
          this.publish('serviceStartFailed', { name, error: error.message });
        }
      }
    }

    console.log('✅ Service startup coordinated');
  }

  /**
   * Coordinate shutdown of all services
   */
  async coordinateShutdown() {
    console.log('🛑 Coordinating service shutdown...');

    const services = Array.from(this.services.entries()).reverse();

    for (const [name, info] of services) {
      const service = info.service;
      
      if (typeof service.stop === 'function') {
        try {
          console.log(`⏸️ Stopping ${name}...`);
          await service.stop();
          this.publish('serviceStopped', { name });
        } catch (error) {
          console.error(`❌ Error stopping ${name}:`, error.message);
        }
      }
    }

    console.log('✅ Service shutdown coordinated');
  }

  /**
   * Graceful shutdown
   */
  async shutdown() {
    console.log('🛑 ProcessLinker shutting down...');
    
    await this.coordinateShutdown();
    
    this.services.clear();
    this.connections.clear();
    this.sharedState.clear();
    this.eventBus.removeAllListeners();
    this.removeAllListeners();
    
    this.state.linked = false;
    
    console.log('✅ ProcessLinker shut down');
  }
}

export default ProcessLinker;
