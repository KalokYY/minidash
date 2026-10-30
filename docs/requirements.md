# Requirements — Track A: Scheduled Orders

## 1. Feature Summary
Customers can place an order now for delivery at a later time. A scheduled order is validated against a lead-time window (45 minutes to 7 days) and the restaurant's opening hours, held in SCHEDULED status, released to the restaurant 30 minutes before delivery, and cancellable until release. All time-dependent logic reads from an injected clock.

**Meanings used below**
- "now" means the current time from the injected clock.
- Timestamps must include a timezone offset and are compared as instants (UTC). Restaurant hours (`opens_at`, `closes_at`, `HH:MM` text) are interpreted as UTC time-of-day, which is a known simplification (see Out of Scope).
- "The release process" is whatever mechanism moves due orders from SCHEDULED to PLACED. How it's triggered is a design decision (see `design.md`).

## 2. User Stories
- **User Story 1:** As a customer, I want to choose a future delivery time when placing an order, so that I can plan my meal around my schedule.
- **User Story 2:** As a customer, I want to cancel a scheduled order before it's released to the restaurant, so that I'm not committed once my plans change.
- **User Story 3:** As a restaurant, I want scheduled orders to appear in my queue only 30 minutes before delivery, so that my kitchen works on what is due now.
- **User Story 4:** As a customer, I want an error message when my requested time is invalid, so that I can fix it without guessing what went wrong.

## 3. Acceptance Criteria (EARS)
### Scheduling window and validation
- **AC-1:** WHEN a customer places an order with a `scheduled_delivery_time` exactly 45 minutes after now and the restaurant is open at that time, THE SYSTEM SHALL accept the order and set its status to SCHEDULED.
- **AC-2:** WHEN a customer places an order with a `scheduled_delivery_time` exactly 7 days after now and the restaurant is open at that time, THE SYSTEM SHALL accept the order and set its status to SCHEDULED.
- **AC-3:** IF the `scheduled_delivery_time` cannot be parsed as a timestamp, has no timezone offset, or is at or before now, THEN THE SYSTEM SHALL reject the order with error `SCHEDULE_INVALID` and create no order.
- **AC-4:** IF the `scheduled_delivery_time` is after now but less than 45 minutes after now, THEN THE SYSTEM SHALL reject the order with error `SCHEDULE_TOO_SOON` and create no order.
- **AC-5:** IF the `scheduled_delivery_time` is more than 7 days after now, THEN THE SYSTEM SHALL reject the order with error `SCHEDULE_TOO_FAR` and create no order.
- **AC-6:** WHEN an order fails more than one scheduling check, THE SYSTEM SHALL report the error of the first failing check in this order: `SCHEDULE_INVALID`, `SCHEDULE_TOO_SOON`, `SCHEDULE_TOO_FAR`, `RESTAURANT_CLOSED`.

### Restaurant opening hours
- **AC-7:** IF the restaurant is closed at the time-of-day of the requested `scheduled_delivery_time`, THEN THE SYSTEM SHALL reject the order with error `RESTAURANT_CLOSED` and create no order. A time equal to `opens_at` or `closes_at` counts as open.

### Hold and release
- **AC-8:** WHEN a customer places a valid scheduled order, THE SYSTEM SHALL set its status to SCHEDULED and not release it immediately.
- **AC-9:** WHEN a customer places an order with no `scheduled_delivery_time`, THE SYSTEM SHALL set its status to PLACED immediately, matching baseline behaviour.
- **AC-10:** WHEN the release process runs and the injected clock is at or after 30 minutes before a SCHEDULED order's delivery time, THE SYSTEM SHALL move that order from SCHEDULED to PLACED exactly once.
- **AC-11:** WHEN the release process runs and the injected clock is earlier than 30 minutes before a SCHEDULED order's delivery time, THE SYSTEM SHALL leave that order in SCHEDULED.
- **AC-12:** WHEN the release process runs again for an order that is already in PLACED, THE SYSTEM SHALL leave its status unchanged and return no error.

### Cancellation
- **AC-13:** WHEN a customer cancels an order whose status is SCHEDULED, THE SYSTEM SHALL set its status to CANCELLED.
- **AC-14:** WHEN the release process runs and an order is CANCELLED, THE SYSTEM SHALL leave it CANCELLED and never release it.
- **AC-15:** IF a customer attempts to cancel an order that is not in SCHEDULED status, THEN THE SYSTEM SHALL reject the request with error `ORDER_NOT_CANCELLABLE` and change nothing.
- **AC-16:** IF a customer attempts to cancel an order that does not exist, THEN THE SYSTEM SHALL respond with 404 not found and change nothing.
- **AC-17:** IF a caller attempts to change an order's status to or from SCHEDULED or CANCELLED through the status endpoint, THEN THE SYSTEM SHALL reject the request with error `STATUS_CHANGE_NOT_ALLOWED` and change nothing.

### Visibility
- **AC-18:** WHEN a customer requests an order, THE SYSTEM SHALL include its `scheduled_delivery_time` in the response, or null if the order is not scheduled.

### Clock
- **AC-19:** THE SYSTEM SHALL obtain the current time from an injected clock dependency rather than the wall clock, so that tests can control time.

## 4. Out of Scope
- Payments and charging for scheduled orders.
- Driver assignment and dispatch.
- Rescheduling an existing scheduled order; only create and cancel are in scope.
- Push, email, or SMS notifications.
- Recurring orders.
- Timezone and DST handling beyond the UTC convention above; restaurant hours are `HH:MM` text interpreted as UTC time-of-day.
- Restaurants open past midnight (`closes_at` earlier than `opens_at`).
- Who is allowed to cancel an order.