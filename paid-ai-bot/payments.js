/**
 * Stripe Payment Integration
 * Handles subscription management, webhook events, and payment processing
 */

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// Pricing configuration
const PRICING_PLANS = {
  basic: {
    id: 'price_basic',
    name: 'Basic Plan',
    price: 9.99,
    tasks_per_month: 1000,
    priority: 'normal'
  },
  pro: {
    id: 'price_pro',
    name: 'Pro Plan',
    price: 29.99,
    tasks_per_month: 5000,
    priority: 'high'
  },
  enterprise: {
    id: 'price_enterprise',
    name: 'Enterprise Plan',
    price: 99.99,
    tasks_per_month: -1, // unlimited
    priority: 'urgent'
  }
};

// In-memory subscription tracking (should use database in production)
const subscriptions = new Map();
const customerUsage = new Map();

/**
 * Initialize payment system
 */
async function initializePayments() {
  if (!process.env.STRIPE_SECRET_KEY) {
    console.warn('⚠️  STRIPE_SECRET_KEY not configured - payment features disabled');
    return;
  }

  try {
    // Verify Stripe connection
    const account = await stripe.accounts.retrieve();
    console.log(`Connected to Stripe account: ${account.id}`);
  } catch (error) {
    console.error('Stripe initialization error:', error.message);
    throw error;
  }
}

/**
 * Create a new customer
 */
async function createCustomer(email, metadata = {}) {
  try {
    const customer = await stripe.customers.create({
      email,
      metadata
    });

    return customer;
  } catch (error) {
    console.error('Create customer error:', error);
    throw error;
  }
}

/**
 * Create a subscription
 */
async function createSubscription(customerId, planId) {
  try {
    const plan = Object.values(PRICING_PLANS).find(p => p.id === planId);
    if (!plan) {
      throw new Error('Invalid plan ID');
    }

    const subscription = await stripe.subscriptions.create({
      customer: customerId,
      items: [{ price: planId }],
      metadata: {
        plan_name: plan.name,
        tasks_limit: plan.tasks_per_month.toString(),
        priority: plan.priority
      }
    });

    // Track subscription
    subscriptions.set(customerId, {
      subscription_id: subscription.id,
      plan: plan,
      status: subscription.status,
      current_period_start: subscription.current_period_start,
      current_period_end: subscription.current_period_end
    });

    // Initialize usage tracking
    customerUsage.set(customerId, {
      tasks_used: 0,
      period_start: subscription.current_period_start,
      period_end: subscription.current_period_end
    });

    return subscription;
  } catch (error) {
    console.error('Create subscription error:', error);
    throw error;
  }
}

/**
 * Cancel a subscription
 */
async function cancelSubscription(subscriptionId) {
  try {
    const subscription = await stripe.subscriptions.cancel(subscriptionId);
    
    // Update local tracking
    for (const [customerId, sub] of subscriptions.entries()) {
      if (sub.subscription_id === subscriptionId) {
        sub.status = 'canceled';
        break;
      }
    }

    return subscription;
  } catch (error) {
    console.error('Cancel subscription error:', error);
    throw error;
  }
}

/**
 * Check if customer can submit task
 */
function canSubmitTask(customerId) {
  const subscription = subscriptions.get(customerId);
  const usage = customerUsage.get(customerId);

  if (!subscription || subscription.status !== 'active') {
    return { allowed: false, reason: 'No active subscription' };
  }

  // Check usage limits
  if (subscription.plan.tasks_per_month !== -1) {
    if (!usage) {
      return { allowed: false, reason: 'Usage not tracked' };
    }

    if (usage.tasks_used >= subscription.plan.tasks_per_month) {
      return { 
        allowed: false, 
        reason: 'Task limit reached',
        tasks_used: usage.tasks_used,
        tasks_limit: subscription.plan.tasks_per_month
      };
    }
  }

  return { 
    allowed: true,
    tasks_remaining: subscription.plan.tasks_per_month === -1 
      ? -1 
      : subscription.plan.tasks_per_month - (usage?.tasks_used || 0)
  };
}

/**
 * Record task usage
 */
function recordTaskUsage(customerId) {
  const usage = customerUsage.get(customerId);
  if (usage) {
    usage.tasks_used += 1;
  }
}

/**
 * Get customer usage stats
 */
function getUsageStats(customerId) {
  const subscription = subscriptions.get(customerId);
  const usage = customerUsage.get(customerId);

  if (!subscription || !usage) {
    return null;
  }

  return {
    plan: subscription.plan.name,
    tasks_used: usage.tasks_used,
    tasks_limit: subscription.plan.tasks_per_month,
    period_start: new Date(usage.period_start * 1000).toISOString(),
    period_end: new Date(usage.period_end * 1000).toISOString(),
    status: subscription.status
  };
}

/**
 * Handle Stripe webhook events
 */
async function handleWebhook(req, res) {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!webhookSecret) {
    console.error('STRIPE_WEBHOOK_SECRET not configured');
    return res.status(500).send('Webhook secret not configured');
  }

  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle the event
  try {
    switch (event.type) {
      case 'customer.subscription.created':
        await handleSubscriptionCreated(event.data.object);
        break;
      
      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object);
        break;
      
      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object);
        break;
      
      case 'invoice.payment_succeeded':
        await handlePaymentSucceeded(event.data.object);
        break;
      
      case 'invoice.payment_failed':
        await handlePaymentFailed(event.data.object);
        break;
      
      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    res.json({ received: true });
  } catch (error) {
    console.error('Webhook handler error:', error);
    res.status(500).send('Webhook handler failed');
  }
}

/**
 * Handle subscription created event
 */
async function handleSubscriptionCreated(subscription) {
  console.log('Subscription created:', subscription.id);
  
  const customerId = subscription.customer;
  const planId = subscription.items.data[0]?.price.id;
  const plan = Object.values(PRICING_PLANS).find(p => p.id === planId);

  if (plan) {
    subscriptions.set(customerId, {
      subscription_id: subscription.id,
      plan: plan,
      status: subscription.status,
      current_period_start: subscription.current_period_start,
      current_period_end: subscription.current_period_end
    });

    customerUsage.set(customerId, {
      tasks_used: 0,
      period_start: subscription.current_period_start,
      period_end: subscription.current_period_end
    });
  }
}

/**
 * Handle subscription updated event
 */
async function handleSubscriptionUpdated(subscription) {
  console.log('Subscription updated:', subscription.id);
  
  const customerId = subscription.customer;
  const existing = subscriptions.get(customerId);

  if (existing) {
    existing.status = subscription.status;
    existing.current_period_start = subscription.current_period_start;
    existing.current_period_end = subscription.current_period_end;
  }
}

/**
 * Handle subscription deleted event
 */
async function handleSubscriptionDeleted(subscription) {
  console.log('Subscription deleted:', subscription.id);
  
  const customerId = subscription.customer;
  const existing = subscriptions.get(customerId);

  if (existing) {
    existing.status = 'canceled';
  }
}

/**
 * Handle successful payment
 */
async function handlePaymentSucceeded(invoice) {
  console.log('Payment succeeded:', invoice.id);
  
  const customerId = invoice.customer;
  const usage = customerUsage.get(customerId);

  if (usage) {
    // Reset usage for new billing period
    usage.tasks_used = 0;
    usage.period_start = invoice.period_start;
    usage.period_end = invoice.period_end;
  }
}

/**
 * Handle failed payment
 */
async function handlePaymentFailed(invoice) {
  console.error('Payment failed:', invoice.id);
  
  // Could send notification to customer
  // Could pause service after X failed payments
  // etc.
}

/**
 * Get pricing plans
 */
function getPricingPlans() {
  return PRICING_PLANS;
}

module.exports = {
  initializePayments,
  createCustomer,
  createSubscription,
  cancelSubscription,
  canSubmitTask,
  recordTaskUsage,
  getUsageStats,
  handleWebhook,
  getPricingPlans
};
