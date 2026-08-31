-- ============================================================
-- URBAN SERVICE OPERATIONS
-- SQL ANALYSIS
-- ============================================================


-- ============================================================
-- QUERY 1: OVERALL BUSINESS KPIs
-- ============================================================

SELECT
    COUNT(*) AS total_bookings,

    SUM(
        CASE
            WHEN Booking_Status = 'Completed'
            THEN 1
            ELSE 0
        END
    ) AS completed_bookings,

    SUM(
        CASE
            WHEN Booking_Status = 'Cancelled'
            THEN 1
            ELSE 0
        END
    ) AS cancelled_bookings,

    SUM(
        CASE
            WHEN Booking_Status = 'Rescheduled'
            THEN 1
            ELSE 0
        END
    ) AS rescheduled_bookings,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN Booking_Status = 'Completed'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS completion_rate,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN Booking_Status = 'Cancelled'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS cancellation_rate

FROM bookings;


-- ============================================================
-- QUERY 2: SERVICE PERFORMANCE
-- ============================================================

SELECT
    Service_Category,

    COUNT(*) AS total_bookings,

    SUM(
        CASE
            WHEN Booking_Status = 'Completed'
            THEN 1
            ELSE 0
        END
    ) AS completed_bookings,

    SUM(
        CASE
            WHEN Booking_Status = 'Cancelled'
            THEN 1
            ELSE 0
        END
    ) AS cancelled_bookings,

    ROUND(
        100.0 *
        SUM(Cancelled_Flag) /
        COUNT(*),
        2
    ) AS cancellation_rate,

    ROUND(
        AVG(Response_Time_Min),
        2
    ) AS avg_response_time,

    ROUND(
        AVG(Customer_Rating),
        2
    ) AS avg_customer_rating

FROM bookings

GROUP BY Service_Category

ORDER BY cancellation_rate DESC;


-- ============================================================
-- QUERY 3: CITY PERFORMANCE
-- ============================================================

SELECT
    City,

    COUNT(*) AS total_bookings,

    SUM(Cancelled_Flag) AS cancelled_bookings,

    ROUND(
        100.0 *
        SUM(Cancelled_Flag) /
        COUNT(*),
        2
    ) AS cancellation_rate,

    ROUND(
        AVG(Response_Time_Min),
        2
    ) AS avg_response_time,

    ROUND(
        AVG(Customer_Rating),
        2
    ) AS avg_customer_rating

FROM bookings

GROUP BY City

ORDER BY cancellation_rate DESC;


-- ============================================================
-- QUERY 4: TIME-SLOT PERFORMANCE
-- ============================================================

SELECT
    Time_Slot,

    COUNT(*) AS total_bookings,

    SUM(Cancelled_Flag) AS cancellations,

    ROUND(
        100.0 *
        SUM(Cancelled_Flag) /
        COUNT(*),
        2
    ) AS cancellation_rate,

    ROUND(
        AVG(Response_Time_Min),
        2
    ) AS avg_response_time

FROM bookings

GROUP BY Time_Slot

ORDER BY
    CASE Time_Slot
        WHEN '8-10 AM' THEN 1
        WHEN '10-12 PM' THEN 2
        WHEN '12-2 PM' THEN 3
        WHEN '2-4 PM' THEN 4
        WHEN '4-6 PM' THEN 5
        WHEN '6-8 PM' THEN 6
        WHEN '8-10 PM' THEN 7
    END;


-- ============================================================
-- QUERY 5: CANCELLATION REASONS
-- ============================================================

SELECT
    Cancellation_Reason,

    COUNT(*) AS cancellations,

    ROUND(
        100.0 *
        COUNT(*) /
        (
            SELECT COUNT(*)
            FROM bookings
            WHERE Booking_Status = 'Cancelled'
        ),
        2
    ) AS percentage_of_cancellations

FROM bookings

WHERE Booking_Status = 'Cancelled'

GROUP BY Cancellation_Reason

ORDER BY cancellations DESC;


-- ============================================================
-- QUERY 6: RESPONSE TIME VS CANCELLATION
-- ============================================================

SELECT

    CASE
        WHEN Response_Time_Min <= 5
            THEN '0-5 min'

        WHEN Response_Time_Min <= 10
            THEN '5-10 min'

        WHEN Response_Time_Min <= 15
            THEN '10-15 min'

        WHEN Response_Time_Min <= 20
            THEN '15-20 min'

        ELSE '20+ min'
    END AS response_time_bucket,

    COUNT(*) AS bookings,

    SUM(Cancelled_Flag) AS cancellations,

    ROUND(
        100.0 *
        SUM(Cancelled_Flag) /
        COUNT(*),
        2
    ) AS cancellation_rate

FROM bookings

GROUP BY response_time_bucket

ORDER BY
    CASE response_time_bucket
        WHEN '0-5 min' THEN 1
        WHEN '5-10 min' THEN 2
        WHEN '10-15 min' THEN 3
        WHEN '15-20 min' THEN 4
        WHEN '20+ min' THEN 5
    END;


-- ============================================================
-- QUERY 7: PEAK VS NON-PEAK
-- ============================================================

SELECT

    CASE
        WHEN Time_Slot IN (
            '4-6 PM',
            '6-8 PM',
            '8-10 PM'
        )
        THEN 'Peak'

        ELSE 'Non-Peak'
    END AS demand_period,

    COUNT(*) AS bookings,

    SUM(Cancelled_Flag) AS cancellations,

    ROUND(
        100.0 *
        SUM(Cancelled_Flag) /
        COUNT(*),
        2
    ) AS cancellation_rate,

    ROUND(
        AVG(Response_Time_Min),
        2
    ) AS avg_response_time

FROM bookings

GROUP BY demand_period;


-- ============================================================
-- QUERY 8: CITY + SERVICE PERFORMANCE
-- ============================================================

SELECT

    City,

    Service_Category,

    COUNT(*) AS bookings,

    SUM(Cancelled_Flag) AS cancellations,

    ROUND(
        100.0 *
        SUM(Cancelled_Flag) /
        COUNT(*),
        2
    ) AS cancellation_rate,

    ROUND(
        AVG(Response_Time_Min),
        2
    ) AS avg_response_time

FROM bookings

GROUP BY
    City,
    Service_Category

HAVING COUNT(*) >= 200

ORDER BY cancellation_rate DESC;


-- ============================================================
-- QUERY 9: PROFESSIONAL PERFORMANCE
-- ============================================================

SELECT

    p.Professional_ID,

    p.City,

    p.Primary_Service,

    p.Experience_Years,

    p.Available_Hours_Per_Week,

    COUNT(b.Booking_ID) AS bookings,

    SUM(b.Completed_Flag) AS completed_bookings,

    ROUND(
        AVG(b.Customer_Rating),
        2
    ) AS avg_customer_rating,

    ROUND(
        AVG(b.Response_Time_Min),
        2
    ) AS avg_response_time

FROM professionals p

LEFT JOIN bookings b
    ON p.Professional_ID = b.Professional_ID

GROUP BY

    p.Professional_ID,
    p.City,
    p.Primary_Service,
    p.Experience_Years,
    p.Available_Hours_Per_Week

ORDER BY bookings DESC;


-- ============================================================
-- QUERY 10: REVENUE BY SERVICE
-- ============================================================

SELECT

    Service_Category,

    COUNT(*) AS completed_orders,

    ROUND(
        SUM(Service_Price),
        0
    ) AS total_revenue,

    ROUND(
        AVG(Service_Price),
        2
    ) AS average_order_value

FROM bookings

WHERE Booking_Status = 'Completed'

GROUP BY Service_Category

ORDER BY total_revenue DESC;