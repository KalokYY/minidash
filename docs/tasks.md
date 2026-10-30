# Implementation Tasks — Track A: Scheduled Orders

The feature will be implemented in small, ordered slices. 
Each slice includes its own tests before moving on to the next one.

## Slice 1: Database and repository changes
- Add the `scheduled_delivery_time` column to the `orders` table.
- Update the repository to save and retrieve the scheduled delivery time.
- Make sure normal orders can still be created with no scheduled delivery time.
- Delete the local `minidash.db` so the app can recreate the database with the updated schema.

**Tests:**
- Verify that a scheduled delivery time is saved and retrieved correctly.
- Verify that a normal order can still be created with a null scheduled delivery time.

## Slice 2: Injected clock
- Create `clock.py` with a Clock object that provides the current UTC time.
- Add a fake clock for tests that can be set to a fixed time.
- Update the existing order service to receive the current time instead of calling `datetime.now()` directly.
- Make sure normal order creation still works.

**Tests:**
- Verify that the clock returns the expected time.
- Verify that order creation uses the injected clock.
- Search the business logic to make sure it does not call the real clock directly.

## Slice 3: Scheduling validation rules
- Add validation for the scheduled delivery time.
- Check that the timestamp is valid and includes a timezone offset.
- Enforce the 45-minute minimum and 7-day maximum.
- Check whether the restaurant is open at the requested time.
- Follow the error-checking order defined in `requirements.md`.
- Add the appropriate scheduling error codes and messages.

**Tests:**
- Test the exact 45-minute and 7-day boundaries.
- Test invalid timestamps, missing timezone offsets, and times at or before now.
- Test times that are too soon or too far ahead.
- Test restaurant opening and closing times.
- Test that the correct error is returned when multiple validation rules fail.

## Slice 4: Create scheduled orders through the API
- Update `POST /orders` to accept an optional `scheduled_delivery_time`.
- Create valid scheduled orders with status `SCHEDULED`.
- Keep normal orders without a scheduled time at status `PLACED`.
- Return the appropriate error response when scheduling validation fails.

**Tests:**
- Test creating a valid scheduled order.
- Test creating a normal order without a scheduled time.
- Test the API responses for invalid scheduled orders.

## Slice 5: Scheduled delivery time in order responses
- Update `GET /orders/{id}` to include `scheduled_delivery_time`.
- Return the scheduled time for scheduled orders.
- Return `null` for orders that were not scheduled.

**Tests:**
- Verify that a scheduled order includes its delivery time.
- Verify that a normal order returns `scheduled_delivery_time: null`.
- Verify that the existing order response fields still work.

## Slice 6: Cancel scheduled orders
- Add `cancel_order()` to the order service.
- Add `POST /orders/{id}/cancel`.
- Allow cancellation only when the order is still `SCHEDULED`.
- Update the order to `CANCELLED` only if it is still scheduled.
- Return the appropriate error when an order cannot be cancelled or does not exist.

**Tests:**
- Verify that a scheduled order can be cancelled.
- Verify that an order that has already been released cannot be cancelled.
- Verify that an already cancelled order cannot be cancelled again.
- Verify that cancelling a nonexistent order returns 404.
- Verify that failed cancellation attempts do not change the order.

## Slice 7: Protect the existing status endpoint
- Update `PATCH /orders/{id}/status`.
- Reject attempts to change an order's status to or from `SCHEDULED` or `CANCELLED`.
- Return `STATUS_CHANGE_NOT_ALLOWED` without changing the order.

**Tests:**
- Verify that attempts to change an order to `SCHEDULED` or `CANCELLED` through the status endpoint are rejected.
- Verify that attempts to change an order from either status are rejected.
- Verify that the existing allowed status changes still work.

## Slice 8: Release due scheduled orders
- Add `release_due_orders(now)` to the order service.
- Release scheduled orders when the injected clock reaches or passes 30 minutes before their delivery time.
- Leave orders scheduled when they are not yet due.
- Ensure only orders still in `SCHEDULED` can be released.
- Make the release operation idempotent so an order is released only once.

**Tests:**
- Verify that an order is released at the 30-minute boundary.
- Verify that an order is released if the clock is later than that boundary.
- Verify that an order remains scheduled before the release time.
- Verify that running the release process again does not change an already released order.
- Verify that cancelled orders are never released.

## Slice 9: Background release loop and integration test
- Add the background release loop to `main.py`.
- Run the release process every 30 seconds.
- Start and stop the loop with the application lifecycle.
- Disable the background loop in regular tests so tests remain predictable.
- Keep the application configured to run with one worker.

**Tests:**
- Verify that the background loop starts and stops with the application.
- Add an integration test that enables the loop and verifies that a due scheduled order moves to `PLACED` without a manual release request.
- Run the full test suite to check that the existing functionality and new scheduled-order feature work together.