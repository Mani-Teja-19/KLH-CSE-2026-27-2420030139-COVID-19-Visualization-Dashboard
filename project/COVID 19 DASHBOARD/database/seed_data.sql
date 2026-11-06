-- =======================================================
-- COVID-19 VISUALIZATION DASHBOARD - SAMPLE DATA INSERT
-- =======================================================

USE `covid19_dashboard`;

-- 1. USERS
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `full_name`, `role`, `phone`, `avatar`, `is_active`, `created_at`) VALUES
(1, 'admin', 'admin@covid19dashboard.gov', 'scrypt:32768:8:1$i1T5o2g4k3...$4589d8...', 'Dr. Rajesh Kumar (Chief Health Officer)', 'Admin', '+91 9876543210', 'default-avatar.png', 1, NOW()),
(2, 'doctor', 'dr.ananya@apollohealth.org', 'scrypt:32768:8:1$i1T5o2g4k3...$4589d8...', 'Dr. Ananya Sen (Infectious Disease Specialist)', 'Doctor', '+91 9811223344', 'default-avatar.png', 1, NOW()),
(3, 'staff', 'healthstaff@district.gov', 'scrypt:32768:8:1$i1T5o2g4k3...$4589d8...', 'Priya Sharma (Field Health Coordinator)', 'Health_Officer', '+91 9844556677', 'default-avatar.png', 1, NOW());

-- 2. HOSPITALS
INSERT INTO `hospitals` (`id`, `name`, `district`, `state`, `total_beds`, `occupied_beds`, `icu_beds`, `occupied_icu`, `oxygen_cylinders`, `helpline`, `address`) VALUES
(1, 'City Apex Covid Care Hospital', 'Central District', 'Maharashtra', 350, 180, 50, 28, 120, '1800-111-999', '45 Health Avenue, Central District'),
(2, 'St. Jude Memorial Hospital', 'North District', 'Maharashtra', 220, 115, 35, 18, 85, '1800-222-888', '12 Ring Road, North District'),
(3, 'Sunrise Community Healthcare Center', 'South District', 'Maharashtra', 180, 92, 25, 12, 60, '1800-333-777', '78 Marine Drive, South District'),
(4, 'Lifeline Multi-Speciality Hospital', 'East District', 'Maharashtra', 300, 145, 40, 22, 110, '1800-444-666', '90 Tech Boulevard, East District'),
(5, 'Valley General Hospital', 'West District', 'Maharashtra', 200, 85, 30, 10, 75, '1800-555-555', '23 Hill View Highway, West District');

-- 3. PLACES
INSERT INTO `places` (`id`, `place_name`, `village_city`, `mandal_taluk`, `district`, `state`, `pincode`, `total_population`, `total_families`, `affected_status`, `positive_cases`, `active_cases`, `recovered_cases`, `death_cases`, `vaccinated_count`, `not_vaccinated_count`) VALUES
(1, 'Green Valley Colony', 'Sector 4', 'Central Taluk', 'Central District', 'Maharashtra', '400001', 18500, 4200, 'Affected', 8, 3, 4, 1, 14, 2),
(2, 'Shivaji Nagar', 'Ward 12', 'North Taluk', 'North District', 'Maharashtra', '400015', 24000, 5600, 'Affected', 12, 5, 6, 1, 18, 3),
(3, 'Lotus Park Heights', 'Urban Ward 8', 'South Taluk', 'South District', 'Maharashtra', '400028', 12000, 2800, 'Affected', 5, 1, 4, 0, 11, 1),
(4, 'Lakeview Enclave', 'East Zone 3', 'East Taluk', 'East District', 'Maharashtra', '400050', 16500, 3900, 'Affected', 6, 2, 3, 1, 13, 2),
(5, 'Pawan Dham Village', 'Rural Block A', 'West Taluk', 'West District', 'Maharashtra', '400072', 8500, 1900, 'Not Affected', 0, 0, 0, 0, 8, 2),
(6, 'Adarsh Nagar', 'Sector 9', 'Central Taluk', 'Central District', 'Maharashtra', '400004', 21000, 4900, 'Affected', 7, 2, 5, 0, 16, 2),
(7, 'Royal Palms Avenue', 'North Zone 2', 'North Taluk', 'North District', 'Maharashtra', '400021', 14200, 3300, 'Affected', 4, 1, 3, 0, 10, 1),
(8, 'Kasturba Hamlet', 'South Block 5', 'South Taluk', 'South District', 'Maharashtra', '400035', 6800, 1500, 'Not Affected', 0, 0, 0, 0, 6, 1);

-- 4. NOTIFICATIONS
INSERT INTO `notifications` (`id`, `title`, `message`, `category`, `alert_level`, `is_read`, `target_url`, `created_at`) VALUES
(1, 'Emergency Containment Alert', 'Shivaji Nagar (North District) declared a micro-containment zone due to 5 active cases in 48 hours.', 'Containment Zone', 'High', 0, '/places', NOW()),
(2, 'High ICU Occupancy Warning', 'City Apex Hospital ICU occupancy reached 85%. Additional ventilator support requested.', 'Emergency', 'High', 0, '/cases', NOW()),
(3, 'Mega Vaccination Drive Complete', 'Successfully administered over 1,200 vaccine doses across East & South district camps.', 'Vaccination', 'Low', 0, '/vaccinations', NOW()),
(4, 'New Recovery Milestone', 'District recovery rate has crossed 88.5% this week with 14 patients safely discharged.', 'Recovery', 'Low', 1, '/cases', NOW()),
(5, 'New Omicron Sub-variant Screened', 'Health laboratory confirmed detection of 2 sub-variant cases; contact tracing initiated.', 'New Case', 'Medium', 1, '/cases', NOW());

-- 5. SETTINGS
INSERT INTO `settings` (`id`, `setting_key`, `setting_value`, `description`, `updated_at`) VALUES
(1, 'app_title', 'COVID-19 Public Health & Visualization Portal', 'Application branding title', NOW()),
(2, 'alert_email_notifications', 'true', 'Enable automated emergency email alerts to district heads', NOW()),
(3, 'containment_threshold_cases', '5', 'Number of active cases in a place triggering containment zone status', NOW()),
(4, 'default_theme', 'dark', 'Default UI color theme (light / dark)', NOW()),
(5, 'auto_refresh_seconds', '60', 'Live dashboard metric polling interval in seconds', NOW());
