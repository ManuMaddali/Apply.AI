/**
 * Subscription Event Manager
 * Handles real-time subscription status updates and event coordination
 */

// Event types
export const SUBSCRIPTION_EVENTS = {
  STATUS_CHANGED: 'subscriptionStatusChanged',
  USAGE_UPDATED: 'usageUpdated',
  TIER_CHANGED: 'tierChanged',
  PAYMENT_UPDATED: 'paymentUpdated',
  SUBSCRIPTION_CANCELLED: 'subscriptionCancelled',
  SUBSCRIPTION_RENEWED: 'subscriptionRenewed',
  SUBSCRIPTION_EXPIRED: 'subscriptionExpired'
};

// Event manager class
class SubscriptionEventManager {
  constructor() {
    this.listeners = new Map();
    this.lastKnownStatus = null;
    this.updateQueue = [];
    this.isProcessingQueue = false;
  }

  /**
   * Subscribe to subscription events
   */
  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType).add(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(eventType);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.listeners.delete(eventType);
        }
      }
    };
  }

  /**
   * Emit subscription event
   */
  emit(eventType, data = {}) {
    const callbacks = this.listeners.get(eventType);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in subscription event callback for ${eventType}:`, error);
        }
      });
    }

    // Also emit to window for backward compatibility
    const customEvent = new CustomEvent(eventType, {
      detail: { ...data, timestamp: new Date().toISOString() }
    });
    window.dispatchEvent(customEvent);
  }

  /**
   * Queue subscription status update
   */
  queueUpdate(updateData) {
    this.updateQueue.push({
      ...updateData,
      timestamp: Date.now()
    });

    if (!this.isProcessingQueue) {
      this.processUpdateQueue();
    }
  }

  /**
   * Process queued updates with debouncing
   */
  async processUpdateQueue() {
    if (this.isProcessingQueue || this.updateQueue.length === 0) {
      return;
    }

    this.isProcessingQueue = true;

    try {
      // Wait a bit to collect more updates
      await new Promise(resolve => setTimeout(resolve, 500));

      // Get the most recent update for each type
      const latestUpdates = new Map();
      this.updateQueue.forEach(update => {
        const key = `${update.type}_${update.userId || 'global'}`;
        if (!latestUpdates.has(key) || latestUpdates.get(key).timestamp < update.timestamp) {
          latestUpdates.set(key, update);
        }
      });

      // Process each unique update
      for (const update of latestUpdates.values()) {
        await this.processUpdate(update);
      }

      // Clear processed updates
      this.updateQueue = [];
    } catch (error) {
      console.error('Error processing subscription update queue:', error);
    } finally {
      this.isProcessingQueue = false;

      // Process any new updates that came in while we were processing
      if (this.updateQueue.length > 0) {
        setTimeout(() => this.processUpdateQueue(), 100);
      }
    }
  }

  /**
   * Process individual subscription update
   */
  async processUpdate(update) {
    const { type, data, previousData } = update;

    try {
      switch (type) {
        case 'subscription_status':
          await this.handleSubscriptionStatusUpdate(data, previousData);
          break;
        case 'usage_update':
          await this.handleUsageUpdate(data, previousData);
          break;
        case 'tier_change':
          await this.handleTierChange(data, previousData);
          break;
        case 'payment_update':
          await this.handlePaymentUpdate(data, previousData);
          break;
        default:
          console.warn('Unknown subscription update type:', type);
      }
    } catch (error) {
      console.error(`Error processing ${type} update:`, error);
    }
  }

  /**
   * Handle subscription status updates
   */
  async handleSubscriptionStatusUpdate(newStatus, previousStatus) {
    // Detect specific changes
    const wasActive = previousStatus?.is_pro_active;
    const isActive = newStatus?.is_pro_active;
    const wasCancelled = previousStatus?.cancel_at_period_end;
    const isCancelled = newStatus?.cancel_at_period_end;

    // Emit general status change
    this.emit(SUBSCRIPTION_EVENTS.STATUS_CHANGED, {
      newStatus,
      previousStatus,
      changes: this.detectStatusChanges(newStatus, previousStatus)
    });

    // Emit specific events
    if (wasActive !== isActive) {
      this.emit(SUBSCRIPTION_EVENTS.TIER_CHANGED, {
        newTier: isActive ? 'pro' : 'free',
        previousTier: wasActive ? 'pro' : 'free',
        isActive,
        wasActive
      });
    }

    if (!wasCancelled && isCancelled) {
      this.emit(SUBSCRIPTION_EVENTS.SUBSCRIPTION_CANCELLED, {
        cancelDate: newStatus.cancel_at_period_end,
        reason: newStatus.cancellation_reason
      });
    }

    if (wasCancelled && !isCancelled) {
      this.emit(SUBSCRIPTION_EVENTS.SUBSCRIPTION_RENEWED, {
        renewalDate: newStatus.current_period_end
      });
    }

    // Check for expiration
    if (newStatus.subscription_status === 'canceled' && previousStatus?.subscription_status !== 'canceled') {
      this.emit(SUBSCRIPTION_EVENTS.SUBSCRIPTION_EXPIRED, {
        expiredAt: new Date().toISOString()
      });
    }

    this.lastKnownStatus = newStatus;
  }

  /**
   * Handle usage updates
   */
  async handleUsageUpdate(newUsage, previousUsage) {
    this.emit(SUBSCRIPTION_EVENTS.USAGE_UPDATED, {
      newUsage,
      previousUsage,
      changes: this.detectUsageChanges(newUsage, previousUsage)
    });
  }

  /**
   * Handle tier changes
   */
  async handleTierChange(newTier, previousTier) {
    this.emit(SUBSCRIPTION_EVENTS.TIER_CHANGED, {
      newTier,
      previousTier,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Handle payment updates
   */
  async handlePaymentUpdate(newPayment, previousPayment) {
    this.emit(SUBSCRIPTION_EVENTS.PAYMENT_UPDATED, {
      newPayment,
      previousPayment,
      changes: this.detectPaymentChanges(newPayment, previousPayment)
    });
  }

  /**
   * Detect changes in subscription status
   */
  detectStatusChanges(newStatus, previousStatus) {
    if (!previousStatus) return { type: 'initial_load' };

    const changes = {};

    if (newStatus.is_pro_active !== previousStatus.is_pro_active) {
      changes.tier_changed = {
        from: previousStatus.is_pro_active ? 'pro' : 'free',
        to: newStatus.is_pro_active ? 'pro' : 'free'
      };
    }

    if (newStatus.subscription_status !== previousStatus.subscription_status) {
      changes.status_changed = {
        from: previousStatus.subscription_status,
        to: newStatus.subscription_status
      };
    }

    if (newStatus.cancel_at_period_end !== previousStatus.cancel_at_period_end) {
      changes.cancellation_changed = {
        from: previousStatus.cancel_at_period_end,
        to: newStatus.cancel_at_period_end
      };
    }

    return changes;
  }

  /**
   * Detect changes in usage data
   */
  detectUsageChanges(newUsage, previousUsage) {
    if (!previousUsage) return { type: 'initial_load' };

    const changes = {};

    if (newUsage.weekly_usage_count !== previousUsage.weekly_usage_count) {
      changes.weekly_usage_changed = {
        from: previousUsage.weekly_usage_count,
        to: newUsage.weekly_usage_count,
        delta: newUsage.weekly_usage_count - previousUsage.weekly_usage_count
      };
    }

    if (newUsage.total_usage_count !== previousUsage.total_usage_count) {
      changes.total_usage_changed = {
        from: previousUsage.total_usage_count,
        to: newUsage.total_usage_count,
        delta: newUsage.total_usage_count - previousUsage.total_usage_count
      };
    }

    return changes;
  }

  /**
   * Detect changes in payment data
   */
  detectPaymentChanges(newPayment, previousPayment) {
    if (!previousPayment) return { type: 'initial_load' };

    const changes = {};

    if (newPayment.payment_method_id !== previousPayment.payment_method_id) {
      changes.payment_method_changed = {
        from: previousPayment.payment_method_id,
        to: newPayment.payment_method_id
      };
    }

    return changes;
  }

  /**
   * Get current subscription status
   */
  getCurrentStatus() {
    return this.lastKnownStatus;
  }

  /**
   * Clear all listeners and reset state
   */
  reset() {
    this.listeners.clear();
    this.lastKnownStatus = null;
    this.updateQueue = [];
    this.isProcessingQueue = false;
  }
}

// Create singleton instance
const subscriptionEventManager = new SubscriptionEventManager();

// Export convenience functions
export const subscribeToSubscriptionEvents = (eventType, callback) => {
  return subscriptionEventManager.subscribe(eventType, callback);
};

export const emitSubscriptionEvent = (eventType, data) => {
  subscriptionEventManager.emit(eventType, data);
};

export const queueSubscriptionUpdate = (updateData) => {
  subscriptionEventManager.queueUpdate(updateData);
};

export const getCurrentSubscriptionStatus = () => {
  return subscriptionEventManager.getCurrentStatus();
};

export const resetSubscriptionEventManager = () => {
  subscriptionEventManager.reset();
};

export default subscriptionEventManager;