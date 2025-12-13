/**
 * feature-manager.js - Unified Feature Controller
 * 
 * Enables/disables features dynamically, manages dependencies between features,
 * and provides runtime configuration for The-basics system.
 */

const fs = require('fs');
const path = require('path');
const EventEmitter = require('events');
const yaml = require('js-yaml');

class FeatureManager extends EventEmitter {
  constructor(configPath = null) {
    super();
    
    this.configPath = configPath || path.join(process.cwd(), 'config', 'features.yaml');
    this.features = new Map();
    this.dependencies = new Map();
    this.loadConfig();
    
    console.log('[FeatureManager] Initialized with', this.features.size, 'features');
  }
  
  loadConfig() {
    try {
      if (fs.existsSync(this.configPath)) {
        const configContent = fs.readFileSync(this.configPath, 'utf8');
        const config = yaml.load(configContent);
        
        if (config && config.features) {
          this.parseConfig(config.features);
          console.log('[FeatureManager] Configuration loaded');
        }
      } else {
        console.log('[FeatureManager] No config file found, using defaults');
        this.initializeDefaults();
      }
    } catch (error) {
      console.error('[FeatureManager] Failed to load config:', error.message);
      this.initializeDefaults();
    }
  }
  
  parseConfig(featuresConfig) {
    for (const [category, settings] of Object.entries(featuresConfig)) {
      if (typeof settings === 'object') {
        for (const [feature, config] of Object.entries(settings)) {
          const featureKey = `${category}.${feature}`;
          
          this.features.set(featureKey, {
            enabled: typeof config === 'boolean' ? config : config.enabled !== false,
            config: typeof config === 'object' ? config : {},
            category,
            name: feature
          });
          
          // Track dependencies if specified
          if (typeof config === 'object' && config.depends_on) {
            this.dependencies.set(featureKey, config.depends_on);
          }
        }
      }
    }
  }
  
  initializeDefaults() {
    const defaults = {
      'trading.enabled': { enabled: false, category: 'trading', name: 'enabled', config: {} },
      'trading.auto_approve': { enabled: false, category: 'trading', name: 'auto_approve', config: {} },
      'ai_platforms.mturk': { enabled: true, category: 'ai_platforms', name: 'mturk', config: {} },
      'ai_platforms.appen': { enabled: true, category: 'ai_platforms', name: 'appen', config: {} },
      'ai_platforms.rapidapi': { enabled: true, category: 'ai_platforms', name: 'rapidapi', config: {} },
      'freelance.upwork': { enabled: false, category: 'freelance', name: 'upwork', config: {} },
      'freelance.fiverr': { enabled: false, category: 'freelance', name: 'fiverr', config: {} },
      'monitoring.prometheus': { enabled: true, category: 'monitoring', name: 'prometheus', config: {} },
      'monitoring.cloudwatch': { enabled: true, category: 'monitoring', name: 'cloudwatch', config: {} }
    };
    
    for (const [key, value] of Object.entries(defaults)) {
      this.features.set(key, value);
    }
  }
  
  /**
   * Check if a feature is enabled
   */
  isEnabled(featureKey) {
    const feature = this.features.get(featureKey);
    
    if (!feature) {
      console.warn(`[FeatureManager] Unknown feature: ${featureKey}`);
      return false;
    }
    
    // Check if enabled
    if (!feature.enabled) {
      return false;
    }
    
    // Check dependencies
    const dependencies = this.dependencies.get(featureKey);
    if (dependencies && Array.isArray(dependencies)) {
      for (const dep of dependencies) {
        if (!this.isEnabled(dep)) {
          console.warn(`[FeatureManager] ${featureKey} disabled due to dependency: ${dep}`);
          return false;
        }
      }
    }
    
    return true;
  }
  
  /**
   * Enable a feature
   */
  enable(featureKey) {
    const feature = this.features.get(featureKey);
    
    if (!feature) {
      console.error(`[FeatureManager] Cannot enable unknown feature: ${featureKey}`);
      return false;
    }
    
    if (feature.enabled) {
      console.log(`[FeatureManager] Feature already enabled: ${featureKey}`);
      return true;
    }
    
    // Check and enable dependencies first
    const dependencies = this.dependencies.get(featureKey);
    if (dependencies && Array.isArray(dependencies)) {
      for (const dep of dependencies) {
        if (!this.isEnabled(dep)) {
          console.log(`[FeatureManager] Enabling dependency: ${dep}`);
          this.enable(dep);
        }
      }
    }
    
    feature.enabled = true;
    console.log(`[FeatureManager] Enabled feature: ${featureKey}`);
    
    this.emit('featureEnabled', featureKey, feature);
    this.saveConfig();
    
    return true;
  }
  
  /**
   * Disable a feature
   */
  disable(featureKey) {
    const feature = this.features.get(featureKey);
    
    if (!feature) {
      console.error(`[FeatureManager] Cannot disable unknown feature: ${featureKey}`);
      return false;
    }
    
    if (!feature.enabled) {
      console.log(`[FeatureManager] Feature already disabled: ${featureKey}`);
      return true;
    }
    
    // Check if any enabled features depend on this one
    const dependents = this.getDependents(featureKey);
    if (dependents.length > 0) {
      console.warn(`[FeatureManager] Disabling dependent features:`, dependents);
      for (const dependent of dependents) {
        this.disable(dependent);
      }
    }
    
    feature.enabled = false;
    console.log(`[FeatureManager] Disabled feature: ${featureKey}`);
    
    this.emit('featureDisabled', featureKey, feature);
    this.saveConfig();
    
    return true;
  }
  
  /**
   * Get features that depend on the given feature
   */
  getDependents(featureKey) {
    const dependents = [];
    
    for (const [key, deps] of this.dependencies.entries()) {
      if (Array.isArray(deps) && deps.includes(featureKey)) {
        const feature = this.features.get(key);
        if (feature && feature.enabled) {
          dependents.push(key);
        }
      }
    }
    
    return dependents;
  }
  
  /**
   * Get feature configuration
   */
  getConfig(featureKey) {
    const feature = this.features.get(featureKey);
    return feature ? feature.config : null;
  }
  
  /**
   * Update feature configuration
   */
  updateConfig(featureKey, config) {
    const feature = this.features.get(featureKey);
    
    if (!feature) {
      console.error(`[FeatureManager] Cannot update config for unknown feature: ${featureKey}`);
      return false;
    }
    
    feature.config = { ...feature.config, ...config };
    console.log(`[FeatureManager] Updated config for: ${featureKey}`);
    
    this.emit('configUpdated', featureKey, feature.config);
    this.saveConfig();
    
    return true;
  }
  
  /**
   * Get all features in a category
   */
  getCategory(category) {
    const categoryFeatures = {};
    
    for (const [key, feature] of this.features.entries()) {
      if (feature.category === category) {
        categoryFeatures[feature.name] = {
          enabled: feature.enabled,
          config: feature.config
        };
      }
    }
    
    return categoryFeatures;
  }
  
  /**
   * Get all enabled features
   */
  getEnabledFeatures() {
    const enabled = [];
    
    for (const [key, feature] of this.features.entries()) {
      if (feature.enabled) {
        enabled.push(key);
      }
    }
    
    return enabled;
  }
  
  /**
   * Save configuration to file
   */
  saveConfig() {
    try {
      const config = { features: {} };
      
      // Group by category
      for (const [key, feature] of this.features.entries()) {
        if (!config.features[feature.category]) {
          config.features[feature.category] = {};
        }
        
        const featureConfig = {
          enabled: feature.enabled,
          ...feature.config
        };
        
        // Add dependencies if they exist
        const deps = this.dependencies.get(key);
        if (deps) {
          featureConfig.depends_on = deps;
        }
        
        config.features[feature.category][feature.name] = featureConfig;
      }
      
      const yamlContent = yaml.dump(config, {
        indent: 2,
        lineWidth: 120
      });
      
      const configDir = path.dirname(this.configPath);
      if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
      }
      
      fs.writeFileSync(this.configPath, yamlContent, 'utf8');
      console.log('[FeatureManager] Configuration saved');
      
    } catch (error) {
      console.error('[FeatureManager] Failed to save config:', error.message);
    }
  }
  
  /**
   * Get system status
   */
  getStatus() {
    const categories = {};
    
    for (const [key, feature] of this.features.entries()) {
      if (!categories[feature.category]) {
        categories[feature.category] = {
          total: 0,
          enabled: 0,
          features: []
        };
      }
      
      categories[feature.category].total++;
      if (feature.enabled) {
        categories[feature.category].enabled++;
      }
      
      categories[feature.category].features.push({
        name: feature.name,
        enabled: feature.enabled,
        hasConfig: Object.keys(feature.config).length > 0
      });
    }
    
    return {
      totalFeatures: this.features.size,
      enabledFeatures: this.getEnabledFeatures().length,
      categories
    };
  }
  
  /**
   * Execute function if feature is enabled
   */
  ifEnabled(featureKey, fn, elseFn = null) {
    if (this.isEnabled(featureKey)) {
      return fn();
    } else if (elseFn) {
      return elseFn();
    }
    return null;
  }
  
  /**
   * Require a feature to be enabled (throws if disabled)
   */
  require(featureKey) {
    if (!this.isEnabled(featureKey)) {
      throw new Error(`Required feature is disabled: ${featureKey}`);
    }
  }
}

// Singleton instance
let instance = null;

module.exports = {
  FeatureManager,
  getInstance: (configPath) => {
    if (!instance) {
      instance = new FeatureManager(configPath);
    }
    return instance;
  },
  createManager: (configPath) => new FeatureManager(configPath)
};

// Add yaml parsing support inline for environments without js-yaml
if (typeof yaml === 'undefined') {
  console.warn('[FeatureManager] js-yaml not available, using JSON fallback');
  
  // Simple YAML parser for basic feature configs
  const yamlFallback = {
    load: (content) => {
      try {
        // Try JSON first
        return JSON.parse(content);
      } catch {
        // Basic YAML parsing (limited)
        const lines = content.split('\n');
        const result = { features: {} };
        let currentCategory = null;
        
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || trimmed.startsWith('#')) continue;
          
          if (trimmed.endsWith(':') && !trimmed.includes('  ')) {
            currentCategory = trimmed.slice(0, -1);
            if (currentCategory !== 'features') {
              result.features[currentCategory] = {};
            }
          } else if (currentCategory && trimmed.includes(':')) {
            const [key, value] = trimmed.split(':').map(s => s.trim());
            if (value === 'true') result.features[currentCategory][key] = true;
            else if (value === 'false') result.features[currentCategory][key] = false;
            else result.features[currentCategory][key] = value;
          }
        }
        
        return result;
      }
    },
    dump: (obj) => JSON.stringify(obj, null, 2)
  };
  
  // Make available if yaml is undefined
  if (typeof module !== 'undefined' && module.exports) {
    // In CommonJS environment, use the fallback internally
    module.exports.yaml = yamlFallback;
  }
}
