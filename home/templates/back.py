{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">

    <!-- ===== SEO META TAGS ===== -->
    <title>Member Dashboard – ELDOPOLY WELFARE</title>
    <meta name="description" content="Access your ELDOPOLY WELFARE member dashboard. View savings, welfare benefits, shares, loans, and community support programs.">
    <meta name="keywords" content="ELDOPOLY WELFARE dashboard, member dashboard, welfare benefits, savings, shares, loans, Eldoret">
    <meta name="robots" content="index, follow">
    <meta name="author" content="ELDOPOLY WELFARE">
    <link rel="canonical" href="https://www.eldopolywelfare.co.ke/dashboard/">

    <!-- ===== FAVICON ===== -->
    <link rel="icon" type="image/x-icon" href="/static/img/favicon.ico">
    <link rel="apple-touch-icon" href="/static/img/apple-touch-icon.png">

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">

    <style>
        :root {
            --welfare-dark-green: #004d26;
            --welfare-maroon: #800000;
            --welfare-gold: #ffcc00;
            --welfare-light-bg: #f5f0eb;
            --welfare-white: #ffffff;
            --welfare-shadow: 0 4px 15px rgba(0, 77, 38, 0.08);
            --welfare-radius: 12px;
            --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --sidebar-width: 260px;
            --header-height: 56px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: var(--welfare-light-bg);
            font-family: 'Inter', sans-serif;
            color: #333;
            overflow-x: hidden;
            -webkit-tap-highlight-color: transparent;
        }

        /* =============================================
                   SIDEBAR – Mobile-first
                   ============================================= */
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: var(--sidebar-width);
            background: linear-gradient(180deg, var(--welfare-dark-green) 0%, #1a3a2a 60%, var(--welfare-maroon) 100%);
            color: white;
            padding-top: 1.5rem;
            z-index: 1050;
            overflow-y: auto;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            transform: translateX(-100%);
            box-shadow: none;
            will-change: transform;
        }

        .sidebar.open {
            transform: translateX(0);
            box-shadow: 4px 0 30px rgba(0, 0, 0, 0.3);
        }

        .sidebar::-webkit-scrollbar {
            width: 3px;
        }
        .sidebar::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
        }
        .sidebar::-webkit-scrollbar-thumb {
            background: var(--welfare-gold);
            border-radius: 4px;
        }

        .sidebar-brand h4 {
            color: var(--welfare-gold);
            font-weight: 800;
            letter-spacing: 1px;
            font-size: 1.15rem;
        }
        .sidebar-brand small {
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.55rem;
            letter-spacing: 2px;
        }

        .sidebar a {
            display: flex;
            align-items: center;
            color: rgba(255, 255, 255, 0.7);
            padding: 10px 18px;
            text-decoration: none;
            transition: all var(--transition);
            font-weight: 500;
            font-size: 0.82rem;
            border-left: 3px solid transparent;
            gap: 10px;
            min-height: 44px;
            -webkit-tap-highlight-color: transparent;
        }

        .sidebar a i {
            width: 20px;
            font-size: 0.95rem;
            flex-shrink: 0;
            text-align: center;
        }

        .sidebar a:hover,
        .sidebar a.active {
            background: rgba(255, 204, 0, 0.08);
            color: var(--welfare-gold) !important;
            border-left: 3px solid var(--welfare-gold);
        }

        .sidebar a:active {
            background: rgba(255, 204, 0, 0.15);
        }

        .sidebar .menu-label {
            font-size: 0.55rem;
            text-transform: uppercase;
            color: rgba(255, 255, 255, 0.3);
            letter-spacing: 1.5px;
            padding: 0 18px;
            margin-top: 1.2rem;
            margin-bottom: 0.3rem;
        }

        .sidebar hr {
            border-color: rgba(255, 255, 255, 0.06);
            margin: 0.6rem 18px;
        }

        .sidebar .btn-gold {
            background: var(--welfare-gold);
            color: var(--welfare-dark-green);
            font-weight: 700;
            font-size: 0.7rem;
            padding: 5px 12px;
            border-radius: 6px;
            border: none;
            transition: all var(--transition);
        }
        .sidebar .btn-gold:hover {
            background: #f5d742;
            color: var(--welfare-dark-green);
        }
        .sidebar .btn-gold:active {
            transform: scale(0.97);
        }

        /* Submenu collapse */
        .sidebar .collapse a {
            padding-left: 42px !important;
            font-size: 0.78rem;
        }

        /* =============================================
                   SIDEBAR OVERLAY (mobile)
                   ============================================= */
        .sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.45);
            z-index: 1040;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            backdrop-filter: blur(2px);
            -webkit-backdrop-filter: blur(2px);
        }

        .sidebar-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        /* =============================================
                   MAIN CONTENT
                   ============================================= */
        .main-content {
            padding: 12px 14px 80px 14px;
            transition: padding 0.3s ease;
            min-height: 100vh;
            width: 100%;
        }

        /* =============================================
                   MOBILE HEADER
                   ============================================= */
        .mobile-header {
            display: flex !important;
            background: linear-gradient(135deg, var(--welfare-dark-green), var(--welfare-maroon));
            color: white;
            padding: 10px 14px;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 1030;
            border-bottom: 3px solid var(--welfare-gold);
            min-height: var(--header-height);
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
        }

        .mobile-header h5 {
            color: var(--welfare-gold);
            font-weight: 800;
            font-size: 1rem;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .mobile-header h5 i {
            font-size: 1.1rem;
        }

        .mobile-header .hamburger-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.4rem;
            padding: 4px 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            transition: background 0.2s;
            -webkit-tap-highlight-color: transparent;
        }

        .mobile-header .hamburger-btn:active {
            background: rgba(255, 255, 255, 0.15);
        }

        /* =============================================
                   WELCOME HEADER
                   ============================================= */
        .welcome-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 8px 12px;
            margin-bottom: 14px;
        }

        .welcome-header h4 {
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--welfare-dark-green);
            margin: 0;
            word-break: break-word;
        }

        .welcome-header .member-badge {
            font-size: 0.65rem;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            flex-wrap: wrap;
        }

        .welcome-header .date-display {
            font-size: 0.7rem;
            padding: 4px 12px;
            background: white;
            border-radius: 20px;
            box-shadow: var(--welfare-shadow);
            border-left: 3px solid var(--welfare-gold);
            display: inline-flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
            flex-shrink: 0;
        }

        /* =============================================
                   ANNOUNCEMENTS (Mobile-optimized)
                   ============================================= */
        .announcements-wrapper {
            margin-bottom: 12px;
        }

        .announcements-wrapper .announce-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
            margin-bottom: 4px;
        }

        .announcements-wrapper .announce-header .left {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .announcements-wrapper .announce-header .left i {
            font-size: 0.85rem;
            color: var(--welfare-gold);
        }

        .announcements-wrapper .announce-header .left span {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--welfare-dark-green);
        }

        .announcements-wrapper .announce-header .badge-count {
            font-size: 0.5rem;
            padding: 0.1rem 0.5rem;
        }

        .announcements-wrapper .announce-body {
            background: white;
            border-radius: 10px;
            padding: 6px 10px;
            box-shadow: var(--welfare-shadow);
            border: 1px solid rgba(255, 204, 0, 0.08);
        }

        .announce-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
            padding: 5px 4px;
            border-bottom: 1px solid rgba(255, 204, 0, 0.05);
            flex-wrap: wrap;
        }

        .announce-item:last-child {
            border-bottom: none;
        }

        .announce-item .info {
            display: flex;
            align-items: center;
            gap: 4px 8px;
            flex-wrap: wrap;
            flex: 1;
            min-width: 0;
        }

        .announce-item .info .name {
            font-weight: 700;
            color: #222;
            font-size: 0.7rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 90px;
        }

        .announce-item .info .deceased {
            color: #666;
            font-size: 0.65rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 80px;
        }

        .announce-item .info .amount-badge {
            background: var(--welfare-dark-green);
            color: white;
            padding: 0.05rem 0.4rem;
            border-radius: 50px;
            font-size: 0.5rem;
            font-weight: 700;
            white-space: nowrap;
        }

        .announce-item .info .status-badge {
            font-size: 0.45rem;
            padding: 0.05rem 0.4rem;
            border-radius: 50px;
            font-weight: 600;
            white-space: nowrap;
        }

        .announce-item .info .status-badge.paid {
            background: #28a745;
            color: white;
        }
        .announce-item .info .status-badge.pending {
            background: #ffc107;
            color: #856404;
        }
        .announce-item .info .status-badge.you {
            background: #6c757d;
            color: white;
        }

        .announce-item .action-btn {
            background: var(--welfare-maroon);
            color: white;
            border: none;
            padding: 2px 10px;
            border-radius: 6px;
            font-size: 0.55rem;
            font-weight: 600;
            transition: all var(--transition);
            white-space: nowrap;
            min-height: 28px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            -webkit-tap-highlight-color: transparent;
        }

        .announce-item .action-btn:active {
            transform: scale(0.95);
        }

        .announce-item .action-btn.retirement {
            background: var(--welfare-dark-green);
        }

        .announce-item .action-btn:disabled {
            opacity: 0.5;
            pointer-events: none;
        }

        /* =============================================
                   STAT CARDS – Mobile-first
                   ============================================= */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 14px;
        }

        .stat-card {
            border: none;
            border-radius: var(--welfare-radius);
            background: var(--welfare-white);
            border-top: 3px solid var(--welfare-gold);
            transition: all var(--transition);
            box-shadow: var(--welfare-shadow);
            padding: 10px 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            min-height: 68px;
        }

        .stat-card:active {
            transform: scale(0.98);
        }

        .stat-card .stat-icon {
            width: 34px;
            height: 34px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            flex-shrink: 0;
        }

        .stat-card .stat-icon.gold {
            background: rgba(255, 204, 0, 0.12);
            color: var(--welfare-gold);
        }
        .stat-card .stat-icon.green {
            background: rgba(0, 77, 38, 0.10);
            color: var(--welfare-dark-green);
        }
        .stat-card .stat-icon.maroon {
            background: rgba(128, 0, 0, 0.10);
            color: var(--welfare-maroon);
        }
        .stat-card .stat-icon.blue {
            background: rgba(13, 110, 253, 0.10);
            color: #0d6efd;
        }
        .stat-card .stat-icon.purple {
            background: rgba(128, 0, 128, 0.08);
            color: #6a0dad;
        }

        .stat-card .stat-info {
            flex: 1;
            min-width: 0;
        }

        .stat-card .stat-label {
            font-size: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            color: #64748b;
            font-weight: 600;
            margin: 0;
            line-height: 1.2;
        }

        .stat-card .stat-value {
            font-size: 0.95rem;
            font-weight: 800;
            color: var(--welfare-dark-green);
            line-height: 1.2;
            margin: 0;
            word-break: break-word;
        }

        /* =============================================
                   PORTFOLIO OVERVIEW (Mobile)
                   ============================================= */
        .portfolio-card {
            border: none;
            border-radius: var(--welfare-radius);
            box-shadow: var(--welfare-shadow);
            background: white;
            margin-bottom: 14px;
            overflow: hidden;
        }

        .portfolio-card .card-header {
            background: white;
            border: none;
            padding: 10px 14px 4px 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 4px;
        }

        .portfolio-card .card-header h6 {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--welfare-dark-green);
            margin: 0;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .portfolio-card .card-header h6 i {
            color: var(--welfare-gold);
        }

        .portfolio-card .card-body {
            padding: 8px 14px 14px 14px;
        }

        .portfolio-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .portfolio-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .portfolio-item .circle-wrap {
            flex-shrink: 0;
            position: relative;
            width: 56px;
            height: 56px;
        }

        .portfolio-item .circle-wrap svg {
            transform: rotate(-90deg);
            width: 56px;
            height: 56px;
        }

        .portfolio-item .circle-wrap .label-pct {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: 700;
            font-size: 0.6rem;
            color: var(--welfare-dark-green);
            line-height: 1;
        }

        .portfolio-item .info h6 {
            font-size: 0.5rem;
            text-transform: uppercase;
            color: #64748b;
            font-weight: 700;
            letter-spacing: 0.3px;
            margin: 0;
        }

        .portfolio-item .info .value {
            font-size: 0.9rem;
            font-weight: 800;
            color: var(--welfare-dark-green);
            margin: 0;
            line-height: 1.2;
        }

        .portfolio-item .info .goal {
            font-size: 0.55rem;
            color: #888;
            margin: 0;
        }

        .portfolio-item .info .value.maroon {
            color: var(--welfare-maroon);
        }

        /* Active refunds inside portfolio */
        .refund-banner {
            background: rgba(255, 204, 0, 0.04);
            border-radius: 8px;
            padding: 8px 12px;
            margin-top: 10px;
            border-left: 3px solid var(--welfare-gold);
        }

        .refund-banner h6 {
            font-size: 0.7rem;
            font-weight: 700;
            color: var(--welfare-dark-green);
            margin: 0 0 4px 0;
        }

        .refund-banner .refund-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 4px;
            padding: 2px 0;
        }

        .refund-banner .refund-item .amount {
            font-weight: 700;
            font-size: 0.8rem;
            color: #222;
        }

        .refund-banner .refund-item .timer {
            font-family: monospace;
            font-size: 0.6rem;
            font-weight: 700;
            color: var(--welfare-maroon);
        }

        .refund-banner .refund-item .cancel-btn {
            background: none;
            border: none;
            color: var(--welfare-maroon);
            font-size: 0.6rem;
            font-weight: 600;
            padding: 2px 6px;
            -webkit-tap-highlight-color: transparent;
        }

        .refund-banner .refund-item .cancel-btn:active {
            opacity: 0.6;
        }

        /* =============================================
                   CARD TABLES (Mobile-optimized)
                   ============================================= */
        .card-table {
            border: none;
            border-radius: var(--welfare-radius);
            overflow: hidden;
            box-shadow: var(--welfare-shadow);
            background: var(--welfare-white);
            margin-bottom: 14px;
        }

        .card-table .card-header {
            background: linear-gradient(135deg, var(--welfare-dark-green), #1a4a2a);
            color: var(--welfare-gold);
            padding: 10px 14px;
            font-weight: 700;
            border: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            flex-wrap: wrap;
            gap: 4px;
        }

        .card-table .card-header .badge-gold {
            background: var(--welfare-gold);
            color: var(--welfare-dark-green);
            font-weight: 700;
            padding: 0.1rem 0.7rem;
            border-radius: 50px;
            font-size: 0.55rem;
            white-space: nowrap;
        }

        /* Table wrapper for horizontal scroll on mobile */
        .table-scroll {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin: 0;
            padding: 0;
        }

        .table-scroll table {
            min-width: 480px;
            width: 100%;
            margin: 0;
        }

        .table-scroll table thead th {
            background: rgba(0, 77, 38, 0.03);
            color: var(--welfare-dark-green);
            font-size: 0.55rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.3px;
            padding: 0.5rem 0.6rem;
            border-bottom: 2px solid rgba(255, 204, 0, 0.06);
            white-space: nowrap;
        }

        .table-scroll table tbody td {
            padding: 0.5rem 0.6rem;
            vertical-align: middle;
            font-size: 0.72rem;
            border-bottom: 1px solid rgba(255, 204, 0, 0.04);
            white-space: nowrap;
        }

        .table-scroll table tbody tr:active {
            background: rgba(255, 204, 0, 0.04);
        }

        .badge-status {
            padding: 0.15rem 0.6rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            white-space: nowrap;
            display: inline-block;
        }
        .badge-status.approved {
            background: var(--welfare-dark-green);
            color: white;
        }
        .badge-status.pending {
            background: var(--welfare-gold);
            color: var(--welfare-dark-green);
        }
        .badge-status.rejected {
            background: var(--welfare-maroon);
            color: white;
        }
        .badge-status.disbursed {
            background: #0d6efd;
            color: white;
        }

        /* =============================================
                   BEREAVEMENT CARD (Mobile)
                   ============================================= */
        .bereavement-card {
            background: white;
            border-radius: var(--welfare-radius);
            border-left: 4px solid var(--welfare-gold);
            box-shadow: var(--welfare-shadow);
            padding: 10px 14px;
            margin-bottom: 10px;
            transition: all var(--transition);
        }

        .bereavement-card .amount {
            font-size: 0.95rem;
            font-weight: 800;
            color: var(--welfare-dark-green);
        }

        .bereavement-card .label {
            font-size: 0.5rem;
            text-transform: uppercase;
            color: #64748b;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        /* =============================================
                   BUTTONS
                   ============================================= */
        .btn-eldo {
            background: linear-gradient(135deg, var(--welfare-dark-green), #1a5a3a);
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 5px 14px;
            transition: all var(--transition);
            font-size: 0.7rem;
            min-height: 34px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            -webkit-tap-highlight-color: transparent;
        }

        .btn-eldo:active {
            transform: scale(0.96);
            background: linear-gradient(135deg, #1a4a2a, var(--welfare-maroon));
        }

        .btn-eldo-sm {
            font-size: 0.6rem;
            padding: 3px 10px;
            min-height: 28px;
        }

        .btn-outline-danger-sm {
            border: 2px solid var(--welfare-maroon);
            color: var(--welfare-maroon);
            background: transparent;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.55rem;
            transition: all var(--transition);
            min-height: 26px;
            display: inline-flex;
            align-items: center;
            gap: 3px;
            -webkit-tap-highlight-color: transparent;
        }

        .btn-outline-danger-sm:active {
            background: var(--welfare-maroon);
            color: white;
            transform: scale(0.96);
        }

        .btn-success-sm {
            background: linear-gradient(135deg, var(--welfare-dark-green), #1a5a3a) !important;
            border: none !important;
            font-size: 0.6rem;
            padding: 3px 12px;
            min-height: 28px;
            border-radius: 6px;
            color: white;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 3px;
            -webkit-tap-highlight-color: transparent;
        }

        .btn-success-sm:active {
            background: linear-gradient(135deg, #1a4a2a, var(--welfare-maroon)) !important;
            color: var(--welfare-gold) !important;
            transform: scale(0.96);
        }

        /* =============================================
                   GUARANTOR REQUESTS (Mobile)
                   ============================================= */
        .guarantor-card {
            background: white;
            border-radius: var(--welfare-radius);
            box-shadow: var(--welfare-shadow);
            padding: 10px 14px;
            margin-bottom: 14px;
            border-left: 3px solid var(--welfare-gold);
        }

        .guarantor-card h6 {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--welfare-dark-green);
            margin: 0 0 6px 0;
        }

        .guarantor-item {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 6px 10px;
            padding: 6px 0;
            border-bottom: 1px solid rgba(0, 0, 0, 0.04);
        }

        .guarantor-item:last-child {
            border-bottom: none;
        }

        .guarantor-item .info {
            font-size: 0.72rem;
            flex: 1;
            min-width: 0;
        }

        .guarantor-item .info .name {
            font-weight: 700;
            color: var(--welfare-maroon);
        }

        .guarantor-item .info .amount {
            font-weight: 700;
            color: var(--welfare-dark-green);
        }

        .guarantor-item .info .purpose {
            font-size: 0.6rem;
            color: #888;
            display: block;
        }

        .guarantor-item .actions {
            display: flex;
            gap: 6px;
            flex-shrink: 0;
        }

        .guarantor-item .actions .btn-accept {
            background: var(--welfare-dark-green);
            color: white;
            border: none;
            padding: 3px 14px;
            border-radius: 6px;
            font-size: 0.6rem;
            font-weight: 600;
            min-height: 30px;
            -webkit-tap-highlight-color: transparent;
        }

        .guarantor-item .actions .btn-accept:active {
            transform: scale(0.95);
        }

        .guarantor-item .actions .btn-reject {
            background: transparent;
            color: var(--welfare-maroon);
            border: 1.5px solid var(--welfare-maroon);
            padding: 3px 14px;
            border-radius: 6px;
            font-size: 0.6rem;
            font-weight: 600;
            min-height: 30px;
            -webkit-tap-highlight-color: transparent;
        }

        .guarantor-item .actions .btn-reject:active {
            background: var(--welfare-maroon);
            color: white;
            transform: scale(0.95);
        }

        /* =============================================
                   LOCK OVERLAY (Mobile)
                   ============================================= */
        .dashboard-lock {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1020;
            padding: 20px;
        }

        .dashboard-lock .lock-card {
            max-width: 320px;
            width: 100%;
            padding: 20px 24px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            text-align: center;
            border: 2px solid rgba(255, 204, 0, 0.3);
        }

        .dashboard-lock .lock-card .lock-icon {
            font-size: 2rem;
            color: var(--welfare-gold);
            margin-bottom: 6px;
        }

        .dashboard-lock .lock-card h5 {
            font-size: 0.95rem;
            font-weight: 800;
            color: var(--welfare-dark-green);
            margin: 0 0 4px 0;
        }

        .dashboard-lock .lock-card p {
            font-size: 0.7rem;
            color: #888;
            margin: 0 0 12px 0;
        }

        .dashboard-lock .lock-card .btn-set-goal {
            background: linear-gradient(135deg, var(--welfare-dark-green), #1a5a3a);
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 0.75rem;
            font-weight: 700;
            width: 100%;
            -webkit-tap-highlight-color: transparent;
        }

        .dashboard-lock .lock-card .btn-set-goal:active {
            transform: scale(0.97);
        }

        /* =============================================
                   XMAS REFUND PROGRESS
                   ============================================= */
        .progress-xmas {
            height: 4px;
            background: #e9edf2;
            border-radius: 10px;
            overflow: hidden;
            flex: 1;
            min-width: 50px;
        }

        .progress-xmas .progress-bar {
            background: linear-gradient(90deg, var(--welfare-dark-green), var(--welfare-gold));
            border-radius: 10px;
            transition: width 0.6s ease;
            height: 100%;
        }

        /* =============================================
                   RECENT SAVINGS + SHARES (Mobile grid)
                   ============================================= */
        .bottom-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .bottom-grid .card-table {
            margin-bottom: 0;
        }

        .bottom-grid .card-table .card-body {
            padding: 6px 10px;
        }

        .bottom-grid .card-table .card-body .saving-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 0;
            border-bottom: 1px solid rgba(0, 0, 0, 0.03);
            font-size: 0.7rem;
        }

        .bottom-grid .card-table .card-body .saving-row:last-child {
            border-bottom: none;
        }

        .bottom-grid .card-table .card-body .saving-row .date {
            color: #888;
            font-size: 0.6rem;
        }

        .bottom-grid .card-table .card-body .saving-row .amount {
            font-weight: 700;
            color: var(--welfare-dark-green);
        }

        .bottom-grid .card-table .card-body .saving-row .download {
            color: var(--welfare-gold);
            font-size: 0.8rem;
        }

        .bottom-grid .card-table .card-body .share-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 8px;
            margin-bottom: 3px;
            background: rgba(0, 0, 0, 0.02);
            border-radius: 6px;
            border-left: 2px solid var(--welfare-gold);
            font-size: 0.7rem;
        }

        .bottom-grid .card-table .card-body .share-row .type {
            font-weight: 600;
            color: #333;
        }

        .bottom-grid .card-table .card-body .share-row .amount {
            font-weight: 700;
            color: var(--welfare-dark-green);
        }

        /* =============================================
                   RESPONSIVE BREAKPOINTS
                   ============================================= */

        /* Tablets & small desktops */
        @media (min-width: 768px) {
            .sidebar {
                transform: translateX(0) !important;
                box-shadow: 2px 0 20px rgba(0, 0, 0, 0.08);
            }

            .sidebar-overlay {
                display: none !important;
            }

            .mobile-header {
                display: none !important;
            }

            .main-content {
                margin-left: var(--sidebar-width);
                padding: 24px 30px 30px 30px;
            }

            .stats-grid {
                grid-template-columns: repeat(4, 1fr);
                gap: 14px;
            }

            .stat-card {
                padding: 14px 18px;
                min-height: 80px;
            }

            .stat-card .stat-value {
                font-size: 1.15rem;
            }

            .portfolio-grid {
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }

            .portfolio-item .circle-wrap {
                width: 70px;
                height: 70px;
            }

            .portfolio-item .circle-wrap svg {
                width: 70px;
                height: 70px;
            }

            .portfolio-item .circle-wrap .label-pct {
                font-size: 0.7rem;
            }

            .portfolio-item .info .value {
                font-size: 1.1rem;
            }

            .bottom-grid {
                grid-template-columns: 1fr 1fr;
                gap: 18px;
            }

            .announce-item .info .name {
                max-width: 140px;
                font-size: 0.8rem;
            }

            .announce-item .info .deceased {
                max-width: 120px;
                font-size: 0.7rem;
            }

            .table-scroll table {
                min-width: auto;
            }

            .table-scroll table thead th,
            .table-scroll table tbody td {
                white-space: normal;
                padding: 0.6rem 0.8rem;
                font-size: 0.75rem;
            }

            .welcome-header h4 {
                font-size: 1.35rem;
            }

            .welcome-header .date-display {
                font-size: 0.8rem;
                padding: 6px 18px;
            }
        }

        @media (min-width: 992px) {
            .main-content {
                padding: 28px 40px 40px 40px;
            }

            .stats-grid {
                gap: 18px;
            }

            .stat-card .stat-value {
                font-size: 1.25rem;
            }

            .portfolio-item .circle-wrap {
                width: 80px;
                height: 80px;
            }

            .portfolio-item .circle-wrap svg {
                width: 80px;
                height: 80px;
            }

            .portfolio-item .circle-wrap .label-pct {
                font-size: 0.8rem;
            }

            .portfolio-item .info .value {
                font-size: 1.2rem;
            }

            .bottom-grid {
                gap: 24px;
            }
        }

        /* Small phones */
        @media (max-width: 480px) {
            .stats-grid {
                grid-template-columns: 1fr 1fr;
                gap: 6px;
            }

            .stat-card {
                padding: 8px 10px;
                min-height: 58px;
                gap: 8px;
            }

            .stat-card .stat-icon {
                width: 28px;
                height: 28px;
                font-size: 0.75rem;
                border-radius: 8px;
            }

            .stat-card .stat-value {
                font-size: 0.8rem;
            }

            .stat-card .stat-label {
                font-size: 0.45rem;
            }

            .portfolio-grid {
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }

            .portfolio-item .circle-wrap {
                width: 44px;
                height: 44px;
            }

            .portfolio-item .circle-wrap svg {
                width: 44px;
                height: 44px;
            }

            .portfolio-item .circle-wrap .label-pct {
                font-size: 0.5rem;
            }

            .portfolio-item .info .value {
                font-size: 0.75rem;
            }

            .portfolio-item .info .goal {
                font-size: 0.5rem;
            }

            .portfolio-item .info h6 {
                font-size: 0.45rem;
            }

            .bottom-grid {
                grid-template-columns: 1fr;
                gap: 12px;
            }

            .welcome-header h4 {
                font-size: 0.95rem;
            }

            .welcome-header .date-display {
                font-size: 0.6rem;
                padding: 3px 10px;
            }

            .announce-item {
                padding: 4px 2px;
            }

            .announce-item .info .name {
                max-width: 60px;
                font-size: 0.6rem;
            }

            .announce-item .info .deceased {
                max-width: 55px;
                font-size: 0.55rem;
            }

            .announce-item .info .amount-badge {
                font-size: 0.45rem;
                padding: 0.05rem 0.3rem;
            }

            .announce-item .action-btn {
                font-size: 0.5rem;
                padding: 2px 8px;
                min-height: 24px;
            }

            .card-table .card-header {
                font-size: 0.65rem;
                padding: 8px 10px;
            }

            .card-table .card-header .badge-gold {
                font-size: 0.5rem;
                padding: 0.05rem 0.5rem;
            }

            .table-scroll table thead th,
            .table-scroll table tbody td {
                font-size: 0.6rem;
                padding: 0.4rem 0.4rem;
            }

            .guarantor-item .info {
                font-size: 0.65rem;
            }

            .guarantor-item .actions .btn-accept,
            .guarantor-item .actions .btn-reject {
                font-size: 0.55rem;
                padding: 2px 10px;
                min-height: 26px;
            }

            .dashboard-lock .lock-card {
                padding: 16px 18px;
                max-width: 280px;
            }

            .dashboard-lock .lock-card h5 {
                font-size: 0.85rem;
            }

            .dashboard-lock .lock-card p {
                font-size: 0.65rem;
            }

            .dashboard-lock .lock-card .btn-set-goal {
                font-size: 0.7rem;
                padding: 6px 16px;
            }

            .refund-banner .refund-item .amount {
                font-size: 0.7rem;
            }

            .refund-banner .refund-item .timer {
                font-size: 0.5rem;
            }

            .mobile-header h5 {
                font-size: 0.85rem;
            }

            .mobile-header .hamburger-btn {
                font-size: 1.2rem;
            }
        }

        /* Extra small phones */
        @media (max-width: 380px) {
            .stats-grid {
                grid-template-columns: 1fr 1fr;
                gap: 4px;
            }

            .stat-card {
                padding: 6px 8px;
                min-height: 50px;
                gap: 6px;
            }

            .stat-card .stat-icon {
                width: 24px;
                height: 24px;
                font-size: 0.65rem;
            }

            .stat-card .stat-value {
                font-size: 0.7rem;
            }

            .stat-card .stat-label {
                font-size: 0.4rem;
            }

            .portfolio-item .circle-wrap {
                width: 38px;
                height: 38px;
            }

            .portfolio-item .circle-wrap svg {
                width: 38px;
                height: 38px;
            }

            .portfolio-item .circle-wrap .label-pct {
                font-size: 0.45rem;
            }

            .portfolio-item .info .value {
                font-size: 0.7rem;
            }

            .welcome-header h4 {
                font-size: 0.85rem;
            }

            .announce-item .info .name {
                max-width: 45px;
                font-size: 0.55rem;
            }

            .announce-item .info .deceased {
                max-width: 40px;
                font-size: 0.5rem;
            }

            .announce-item .action-btn {
                font-size: 0.45rem;
                padding: 1px 6px;
                min-height: 20px;
            }
        }

        /* =============================================
                   UTILITY HELPERS
                   ============================================= */
        .text-welfare-green {
            color: var(--welfare-dark-green);
        }
        .text-welfare-maroon {
            color: var(--welfare-maroon);
        }
        .text-welfare-gold {
            color: var(--welfare-gold);
        }

        .timer-text {
            color: var(--welfare-maroon);
            font-weight: 700;
            font-family: monospace;
        }

        .collapse-icon {
            transition: transform 0.3s ease;
            display: inline-block;
        }
        .collapse-icon.rotated {
            transform: rotate(180deg);
        }

        /* =============================================
                   TOAST CONTAINER
                   ============================================= */
        #toast-container {
            position: fixed;
            top: 12px;
            right: 12px;
            left: 12px;
            z-index: 9999;
            pointer-events: none;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 6px;
        }

        @media (min-width: 576px) {
            #toast-container {
                top: 20px;
                right: 20px;
                left: auto;
            }
        }

        .sms-popup {
            pointer-events: auto;
            background: white;
            border-radius: 10px;
            padding: 10px 14px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            min-width: 0;
            width: 100%;
            max-width: 380px;
            transform: translateX(120%);
            opacity: 0;
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            border-left: 5px solid var(--welfare-dark-green);
        }

        .sms-popup.show {
            transform: translateX(0);
            opacity: 1;
        }

        .sms-popup .icon {
            font-size: 1.2rem;
            flex-shrink: 0;
        }

        .sms-popup .msg {
            flex: 1;
            min-width: 0;
        }

        .sms-popup .msg strong {
            display: block;
            font-size: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #999;
        }

        .sms-popup .msg span {
            font-size: 0.8rem;
            font-weight: 600;
            color: #222;
            word-break: break-word;
        }

        .sms-popup .close-btn {
            background: none;
            border: none;
            color: #aaa;
            font-size: 0.8rem;
            padding: 4px;
            flex-shrink: 0;
            cursor: pointer;
            -webkit-tap-highlight-color: transparent;
        }

        .sms-popup .close-btn:active {
            color: #666;
        }

        /* Toast color variants */
        .sms-popup.success {
            border-left-color: var(--welfare-dark-green);
        }
        .sms-popup.success .icon {
            color: var(--welfare-dark-green);
        }

        .sms-popup.danger {
            border-left-color: var(--welfare-maroon);
        }
        .sms-popup.danger .icon {
            color: var(--welfare-maroon);
        }

        .sms-popup.info {
            border-left-color: #0d6efd;
        }
        .sms-popup.info .icon {
            color: #0d6efd;
        }

        .sms-popup.warning {
            border-left-color: var(--welfare-gold);
        }
        .sms-popup.warning .icon {
            color: var(--welfare-gold);
        }
    </style>
</head>
<body>

    <!-- ===== SIDEBAR OVERLAY (mobile) ===== -->
    <div class="sidebar-overlay" id="sidebarOverlay"></div>

    <!-- ===== SIDEBAR ===== -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-brand p-3 mb-1 text-center">
            <h4 class="fw-bold"><i class="fas fa-hands-helping me-2"></i> ELDOPOLY</h4>
            <small>WELFARE PORTAL v2.0</small>
        </div>

        {% if request.user.user_type != '4' %}
        <div class="px-3 mb-2">
            {% if 'admin' in request.path or 'management' in request.path or 'staff' in request.path %}
            <a href="{% url 'member_dashboard' %}" class="btn btn-sm w-100 btn-gold fw-bold py-1 shadow-sm">
                <i class="fas fa-user me-2"></i> My Member View
            </a>
            {% else %}
            <a href="{% url 'management_index' %}" class="btn btn-sm w-100 btn-gold fw-bold py-1 shadow-sm">
                <i class="fas fa-user-shield me-2"></i> Management Hub
            </a>
            {% endif %}
        </div>
        {% endif %}

        <div class="menu-label">Main Menu</div>

        <a href="{% url 'member_dashboard' %}" class="{% if request.resolver_match.url_name == 'member_dashboard' %}active{% endif %}">
            <i class="fas fa-th-large"></i> Dashboard
        </a>
        <a href="{% url 'member_profile' %}">
            <i class="fas fa-user"></i> My Profile
        </a>
        <a href="{% url 'deposit_savings' %}" class="{% if 'savings' in request.path %}active{% endif %}">
            <i class="fas fa-piggy-bank"></i> Welfare Savings
        </a>
        <a href="{% url 'purchase_shares' %}" class="{% if 'shares' in request.path %}active{% endif %}">
            <i class="fas fa-chart-pie"></i> Shares
        </a>

        <div class="menu-label">Welfare Services</div>

        <a href="{% url 'apply_loan' %}"><i class="fas fa-file-invoice-dollar"></i> Apply loan</a>
        <a href="{% url 'apply_xmas_loan' %}"><i class="fas fa-holly-berry"></i> Apply Xmas Loan</a>
        <a href="{% url 'pay_loan' %}"><i class="fas fa-hand-holding-usd"></i> Repay Loan</a>
        <a href="{% url 'my_loans' %}"><i class="fas fa-exchange-alt"></i> My Loans</a>

        <div class="menu-label">Records &amp; Reports</div>

        <a href="{% url 'my_statement' %}"><i class="fas fa-file-alt"></i> My Statement</a>
        <a href="{% url 'member_individual_report' %}"><i class="fas fa-book"></i> My Ledger</a>

        <a class="d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#bereavementSubmenu" role="button" aria-expanded="false">
            <span><i class="fas fa-hand-holding-heart"></i> Bereavement</span>
            <i class="fas fa-chevron-down" style="font-size: 0.6rem;"></i>
        </a>
        <div class="collapse" id="bereavementSubmenu">
            <a href="{% url 'pay_bereavement_mpesa' %}" class="ps-5 py-1" style="font-size: 0.78rem;">
                <i class="fas fa-gift me-2"></i> Pay
            </a>
        </div>

        <a class="d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#retirementSubmenu" role="button" aria-expanded="false">
            <span><i class="fas fa-user-clock"></i> Retirement</span>
            <i class="fas fa-chevron-down" style="font-size: 0.6rem;"></i>
        </a>
        <div class="collapse" id="retirementSubmenu">
            <a href="{% url 'pay_retirement_mpesa' %}" class="ps-5 py-1" style="font-size: 0.78rem;">
                <i class="fas fa-gift me-2"></i> Pay
            </a>
        </div>

        <a class="d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#refundSubmenu" role="button" aria-expanded="false">
            <span><i class="fas fa-undo-alt"></i> Refunds</span>
            <i class="fas fa-chevron-down" style="font-size: 0.6rem;"></i>
        </a>
        <div class="collapse" id="refundSubmenu">
            <a href="{% url 'apply_xmas_refund' %}" class="ps-5 py-1" style="font-size: 0.78rem;">
                <i class="fas fa-gift me-2"></i> Holiday Refunds
            </a>
            <a href="{% url 'apply_share_refund' %}" class="ps-5 py-1" style="font-size: 0.78rem;">
                <i class="fas fa-coins me-2"></i> Share Refunds
            </a>
        </div>

        <hr>
        <a href="{% url 'Logout' %}" style="color: rgba(255,255,255,0.5);">
            <i class="fas fa-sign-out-alt"></i> Logout
        </a>
    </div>

    <!-- ===== TOAST CONTAINER ===== -->
    <div id="toast-container"></div>

    <!-- ===== MOBILE HEADER ===== -->
    <header class="mobile-header shadow-sm">
        <h5><i class="fas fa-hands-helping me-1"></i>ELDOPOLY</h5>
        <button class="hamburger-btn" id="sidebarToggle" aria-label="Toggle navigation menu">
            <i class="fas fa-bars"></i>
        </button>
    </header>

    <!-- ===== MAIN CONTENT ===== -->
    <main class="main-content position-relative" id="mainContent">

        <!-- Dashboard Lock -->
        {% if share_goal <= 0 %}
        <div class="dashboard-lock" id="dashboardLock">
            <div class="lock-card">
                <div class="lock-icon"><i class="fas fa-lock"></i></div>
                <h5>Dashboard Locked</h5>
                <p>Set a target share goal to view your full portfolio.</p>
                <button type="button" class="btn-set-goal" onclick="updateGoal('share')">Set Share Goal Now</button>
            </div>
        </div>
        {% endif %}

        <!-- ===== WELCOME HEADER ===== -->
        <div class="welcome-header">
            <div>
                <h4>Hello, {{ profile.user.get_full_name|default:profile.user.username }}!</h4>
                <div class="member-badge">
                    <span class="fw-bold text-welfare-maroon">#{{ profile.membership_number }}</span>
                    <span class="badge bg-success ms-1" style="font-size: 0.55rem; padding: 0.15rem 0.5rem;">Active</span>
                </div>
            </div>
            <div class="date-display">
                <i class="fas fa-calendar-check me-1 text-welfare-gold"></i> {% now "F j, Y" %}
            </div>
        </div>

        <!-- ============================================= -->
        <!-- ===== ANNOUNCEMENTS (Ultra Compact) ===== -->
        <!-- ============================================= -->
        {% with total_announcements=active_bereavements|length|add:active_retirements|length %}
        <div class="announcements-wrapper">
            <div class="announce-header">
                <div class="left">
                    <i class="fas fa-bullhorn"></i>
                    <span>Announcements</span>
                    <span class="badge bg-primary badge-count">{{ total_announcements }}</span>
                </div>
                {% if total_announcements > 0 %}
                <button class="btn btn-sm btn-outline-secondary py-0 px-2" type="button" data-bs-toggle="collapse" data-bs-target="#announcementsCollapse" aria-expanded="true" style="border: none; background: transparent; color: #888; font-size: 0.7rem;">
                    <i class="fas fa-chevron-up collapse-icon" style="font-size: 0.6rem;"></i>
                </button>
                {% endif %}
            </div>

            <div class="collapse show" id="announcementsCollapse">
                <div class="announce-body">
                    <!-- Bereavement -->
                    {% if active_bereavements %}
                    <div style="margin-bottom: 4px;">
                        <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 2px;">
                            <i class="fas fa-heart text-welfare-maroon" style="font-size: 0.6rem;"></i>
                            <span style="font-weight: 700; color: var(--welfare-maroon); font-size: 0.6rem;">Bereavement</span>
                            <span class="badge bg-danger text-white" style="font-size: 0.45rem; padding: 0.05rem 0.4rem;">{{ active_bereavements|length }}</span>
                        </div>
                        {% for item in active_bereavements|slice:":3" %}
                        <div class="announce-item">
                            <div class="info">
                                <span class="name">{{ item.mourner.user.get_full_name|default:item.mourner.user.username }}</span>
                                <span class="deceased">{{ item.deceased_name }}</span>
                                <span class="amount-badge">KES {{ item.monthly_amount|floatformat:0 }}</span>
                                {% if item.is_owner %}
                                <span class="status-badge you">You</span>
                                {% elif item.paid_this_month %}
                                <span class="status-badge paid">Paid</span>
                                {% else %}
                                <span class="status-badge pending">Pending</span>
                                {% endif %}
                            </div>
                            <div>
                                {% if not item.is_owner and not item.paid_this_month %}
                                <button class="action-btn" onclick="payBereavement({{ item.announcement.id }}, '{{ item.deceased_name }}', {{ item.monthly_amount }})">
                                    <i class="fas fa-mobile-alt me-1"></i> Pay
                                </button>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                        {% if active_bereavements|length > 3 %}
                        <div class="text-end mt-1">
                            <a href="{% url 'pay_bereavement_mpesa' %}" style="font-size: 0.55rem; color: var(--welfare-dark-green); font-weight: 600;">View all {{ active_bereavements|length }} →</a>
                        </div>
                        {% endif %}
                    </div>
                    {% endif %}

                    <!-- Retirement -->
                    {% if active_retirements %}
                    <div>
                        <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 2px; margin-top: 4px;">
                            <i class="fas fa-user-clock text-welfare-dark-green" style="font-size: 0.6rem;"></i>
                            <span style="font-weight: 700; color: var(--welfare-dark-green); font-size: 0.6rem;">Retirement</span>
                            <span class="badge bg-primary text-white" style="font-size: 0.45rem; padding: 0.05rem 0.4rem;">{{ active_retirements|length }}</span>
                        </div>
                        {% for item in active_retirements|slice:":3" %}
                        <div class="announce-item">
                            <div class="info">
                                <span class="name">{{ item.retiree.user.get_full_name|default:item.retiree.user.username }}</span>
                                <span style="color: #888; font-size: 0.6rem;">{{ item.retirement_date|date:"d M" }}</span>
                                <span class="amount-badge" style="background: var(--welfare-dark-green);">KES {{ item.monthly_amount|floatformat:0 }}</span>
                                {% if item.is_owner %}
                                <span class="status-badge you">You</span>
                                {% elif item.paid_this_month %}
                                <span class="status-badge paid">Paid</span>
                                {% else %}
                                <span class="status-badge pending">Pending</span>
                                {% endif %}
                            </div>
                            <div>
                                {% if not item.is_owner and not item.paid_this_month %}
                                <button class="action-btn retirement" onclick="payRetirement({{ item.announcement.id }}, '{{ item.retiree.user.get_full_name }}', {{ item.monthly_amount }})">
                                    <i class="fas fa-mobile-alt me-1"></i> Pay
                                </button>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                        {% if active_retirements|length > 3 %}
                        <div class="text-end mt-1">
                            <a href="{% url 'pay_retirement_mpesa' %}" style="font-size: 0.55rem; color: var(--welfare-dark-green); font-weight: 600;">View all {{ active_retirements|length }} →</a>
                        </div>
                        {% endif %}
                    </div>
                    {% endif %}

                    {% if total_announcements == 0 %}
                    <div class="text-center py-1 text-muted" style="font-size: 0.6rem;">
                        <i class="fas fa-check-circle me-1 text-success"></i> No pending announcements
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endwith %}

        <!-- ============================================= -->
        <!-- ===== PORTFOLIO OVERVIEW ===== -->
        <!-- ============================================= -->
        <div class="portfolio-card" id="main-portfolio-card" {% if share_goal <= 0 %}style="pointer-events: none; opacity: 0.5;"{% endif %}>
            <div class="card-header">
                <h6><i class="fas fa-chart-pie me-1"></i>Portfolio Overview</h6>
                <div class="dropdown">
                    <button class="btn btn-light btn-sm rounded-pill px-2" type="button" data-bs-toggle="dropdown" style="font-size: 0.6rem; border: 1px solid #e9edf2; padding: 2px 10px; min-height: 28px;">
                        <i class="fas fa-cog me-1"></i> Targets
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end shadow border-0 rounded-2">
                        <li><button class="dropdown-item small" onclick="updateGoal('share')">Edit Share Goal</button></li>
                        <li><button class="dropdown-item small" onclick="updateGoal('saving')">Edit Savings Target</button></li>
                    </ul>
                </div>
            </div>

            <div class="card-body">
                <div class="portfolio-grid">
                    <!-- Shares -->
                    <div class="portfolio-item">
                        <div class="circle-wrap">
                            <svg viewBox="0 0 120 120">
                                <circle cx="60" cy="60" r="54" fill="none" stroke="#e9ecef" stroke-width="12" />
                                <circle cx="60" cy="60" r="54" fill="none" stroke="#004d26" stroke-width="12"
                                stroke-dasharray="339.29" stroke-dashoffset="{{ dash_offset|default:339.29 }}"
                                stroke-linecap="round" />
                            </svg>
                            <span class="label-pct">{{ share_progress_pct|floatformat:0 }}%</span>
                        </div>
                        <div class="info">
                            <h6>Shares</h6>
                            <p class="value">KES {{ total_shares|floatformat:0 }}</p>
                            <p class="goal">Goal: {{ share_goal|floatformat:0 }}</p>
                        </div>
                    </div>

                    <!-- Savings -->
                    <div class="portfolio-item">
                        <div class="circle-wrap">
                            <svg viewBox="0 0 120 120">
                                <circle cx="60" cy="60" r="54" fill="none" stroke="#e9ecef" stroke-width="12" />
                                <circle cx="60" cy="60" r="54" fill="none" stroke="#800000" stroke-width="12"
                                stroke-dasharray="339.29" stroke-dashoffset="{{ saving_dash_offset|default:339.29 }}"
                                stroke-linecap="round" />
                            </svg>
                            <span class="label-pct">{{ progress_pct|floatformat:0 }}%</span>
                        </div>
                        <div class="info">
                            <h6>Savings</h6>
                            <p class="value maroon">KES {{ current_month_savings|floatformat:0 }}</p>
                            <p class="goal">Target: {{ saving_target|floatformat:0 }}</p>
                        </div>
                    </div>
                </div>

                <!-- Active Share Refunds -->
                {% if active_refunds %}
                <div class="refund-banner">
                    <h6><i class="fas fa-clock me-1 text-welfare-gold"></i>Active Share Refunds</h6>
                    {% for refund in active_refunds %}
                    <div class="refund-item">
                        <span class="amount">KES {{ refund.amount_requested|floatformat:2 }}</span>
                        <span class="timer" id="timer-{{ refund.id }}">--:--:--:--</span>
                        <form action="{% url 'cancel_share_refund' refund.id %}" method="POST" class="d-inline">
                            {% csrf_token %}
                            <button type="submit" class="cancel-btn">Cancel <i class="fas fa-times-circle ms-1"></i></button>
                        </form>
                    </div>
                    <script>
                        (function() {
                            let timeLeft = parseInt("{{ refund.time_remaining|floatformat:0 }}");
                            const display = document.getElementById("timer-{{ refund.id }}");
                            const update = () => {
                                if (timeLeft <= 0) { display.innerHTML = "COMPLETED"; return; }
                                const d = Math.floor(timeLeft / 86400),
                                    h = Math.floor((timeLeft % 86400) / 3600);
                                const m = Math.floor((timeLeft % 3600) / 60),
                                    s = timeLeft % 60;
                                display.innerHTML = d + "d " + h + "h " + m + "m " + s + "s";
                                timeLeft--;
                            };
                            update();
                            setInterval(update, 1000);
                        })();
                    </script>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </div>

        <!-- ============================================= -->
        <!-- ===== XMAS REFUND SECTION ===== -->
        <!-- ============================================= -->
        {% if xmas_refunds %}
        <div class="card-table">
            <div class="card-header">
                <span style="font-size: 0.75rem;"><i class="fas fa-gift me-1" style="color: var(--welfare-gold);"></i> Holiday Refund Requests</span>
                <span class="badge-gold">{{ xmas_refunds|length }} Requests</span>
            </div>
            <div class="table-scroll">
                <table class="table align-middle mb-0">
                    <thead>
                        <tr>
                            <th class="ps-3" style="font-size: 0.55rem;">Refund Details</th>
                            <th style="font-size: 0.55rem;">Amount</th>
                            <th style="font-size: 0.55rem;">Progress</th>
                            <th class="text-center" style="font-size: 0.55rem;">Status</th>
                            <th class="text-end pe-3" style="font-size: 0.55rem;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for refund in xmas_refunds %}
                        <tr>
                            <td class="ps-3">
                                <div style="font-weight: 700; color: var(--welfare-dark-green); font-size: 0.72rem;">
                                    <i class="fas fa-gift me-1" style="color: var(--welfare-gold);"></i> Holiday Refund
                                </div>
                                <small class="text-muted" style="font-size: 0.55rem;">Applied: {{ refund.date_applied|date:"d M, Y" }}</small>
                            </td>
                            <td style="font-weight: 700; color: var(--welfare-dark-green); font-size: 0.78rem;">KES {{ refund.amount_requested|floatformat:2 }}</td>
                            <td>
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <div class="progress-xmas" style="width: 70px;">
                                        <div class="progress-bar" role="progressbar" style="width: {{ refund.progress_percent }}%;"></div>
                                    </div>
                                    <span style="font-weight: 700; font-size: 0.6rem; color: var(--welfare-dark-green);">
                                        {{ refund.approvals_count }}/3
                                    </span>
                                </div>
                                <small class="text-muted d-block mt-1" style="font-size: 0.5rem;">
                                    {{ refund.current_stage }}
                                </small>
                            </td>
                            <td class="text-center">
                                <span class="badge-status 
                                          {% if refund.status == 'disbursed' %}approved
                                          {% elif refund.status == 'approved' %}approved
                                          {% elif refund.status == 'rejected' %}rejected
                                          {% else %}pending{% endif %}">
                                    {{ refund.get_status_display|default:"Pending" }}
                                </span>
                            </td>
                            <td class="text-end pe-3">
                                {% if refund.can_cancel %}
                                <form action="{% url 'cancel_xmas_refund' refund.id %}" method="POST" class="d-inline">
                                    {% csrf_token %}
                                    <button type="submit" class="btn-outline-danger-sm" onclick="return confirm('Cancel this refund request?')">
                                        <i class="fas fa-times me-1"></i> Cancel
                                    </button>
                                </form>
                                {% elif refund.status == 'disbursed' %}
                                <span class="text-success fw-bold" style="font-size: 0.6rem;">
                                    <i class="fas fa-check-circle me-1"></i> Disbursed
                                </span>
                                {% else %}
                                <span class="text-muted" style="font-size: 0.6rem;">
                                    <i class="fas fa-clock me-1"></i> In Progress
                                </span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- ============================================= -->
        <!-- ===== GUARANTOR REQUESTS ===== -->
        <!-- ============================================= -->
        {% if pending_guarantor_requests %}
        <div class="guarantor-card">
            <h6><i class="fas fa-user-shield me-1 text-welfare-gold"></i>Guarantor Requests</h6>
            {% for g in pending_guarantor_requests %}
            <div class="guarantor-item">
                <div class="info">
                    <span class="name">{{ g.loan.member.user.get_full_name }}</span>
                    wants you to guarantee <span class="amount">KES {{ g.guaranteed_amount|floatformat:2 }}</span>
                    <span class="purpose">Purpose: {{ g.loan.purpose }}</span>
                </div>
                <div class="actions">
                    <a href="{% url 'respond_guarantor' g.id 'accept' %}" class="btn-accept">Accept</a>
                    <a href="{% url 'respond_guarantor' g.id 'reject' %}" class="btn-reject">Reject</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- ============================================= -->
        <!-- ===== STATS ROW ===== -->
        <!-- ============================================= -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon gold"><i class="fas fa-chart-pie"></i></div>
                <div class="stat-info">
                    <div class="stat-label">Total Shares</div>
                    <div class="stat-value">KES {{ total_shares|default:"0"|floatformat:0 }}</div>
                </div>
            </div>
            <div class="stat-card" style="border-top-color: var(--welfare-dark-green);">
                <div class="stat-icon green"><i class="fas fa-piggy-bank"></i></div>
                <div class="stat-info">
                    <div class="stat-label">Total Xmas Savings</div>
                    <div class="stat-value">KES {{ total_savings|floatformat:0 }}</div>
                </div>
            </div>
            <div class="stat-card" style="border-top-color: var(--welfare-maroon);">
                <div class="stat-icon maroon"><i class="fas fa-hand-holding-usd"></i></div>
                <div class="stat-info">
                    <div class="stat-label">Loan Balance</div>
                    <div class="stat-value" style="color: var(--welfare-maroon);">KES {{ total_loans|floatformat:0 }}</div>
                </div>
            </div>
            <div class="stat-card" style="border-top-color: #0d6efd;">
                <div class="stat-icon blue"><i class="fas fa-exclamation-triangle"></i></div>
                <div class="stat-info">
                    <div class="stat-label">Penalties</div>
                    <div class="stat-value" style="color: #0d6efd;">KES {{ total_penalties|floatformat:0 }}</div>
                </div>
            </div>
        </div>

        <!-- ============================================= -->
        <!-- ===== XMAS LOANS TABLE (UPDATED with Details column) ===== -->
        <!-- ============================================= -->
        {% if xmas_loans %}
        <div class="card-table">
            <div class="card-header">
                <span style="font-size: 0.75rem;"><i class="fas fa-holly-berry me-1"></i> My Xmas loan Portfolio</span>
                <span class="badge-gold">{{ active_xmas_count }} Active</span>
            </div>
            <div class="table-scroll">
                <table class="table align-middle mb-0">
                    <thead>
                        <tr>
                            <th class="ps-3" style="font-size: 0.55rem;">Loan Details</th>
                            <th style="font-size: 0.55rem;">Principal</th>
                            <th style="font-size: 0.55rem;">Remaining</th>
                            <th class="text-center" style="font-size: 0.55rem;">Status</th>
                            <th class="text-center" style="font-size: 0.55rem;">Action</th>
                            <th class="text-center" style="font-size: 0.55rem;">Details</th> <!-- NEW -->
                        </tr>
                    </thead>
                    <tbody>
                        {% for xl in xmas_loans %}
                        <tr>
                            <td class="ps-3">
                                <div style="font-weight: 700; color: var(--welfare-dark-green); font-size: 0.72rem;">QW-{{ xl.id|stringformat:"04d" }}</div>
                                <small class="text-muted" style="font-size: 0.55rem;">{{ xl.application_date|date:"d M, Y" }}</small>
                            </td>
                            <td style="font-weight: 700; font-size: 0.78rem;">KES {{ xl.amount_requested|floatformat:0 }}</td>
                            <td style="color: var(--welfare-maroon); font-weight: 700; font-size: 0.78rem;">KES {{ xl.remaining_balance|default:"0"|floatformat:0 }}</td>
                            <td class="text-center">
                                <span class="badge-status {% if xl.status == 'approved' or xl.status == 'disbursed' %}approved{% elif xl.status == 'rejected' %}rejected{% else %}pending{% endif %}">
                                    {{ xl.get_status_display }}
                                </span>
                            </td>
                            <td class="text-center">
                                {% if xl.status == 'disbursed' %}
                                <a href="{% url 'pay_xmas_loan' %}" class="btn-eldo btn-eldo-sm">Repay</a>
                                {% else %}
                                <small class="text-muted" style="font-size: 0.6rem;">In Review</small>
                                {% endif %}
                            </td>
                            <td class="text-center">
                                <button class="btn btn-sm btn-outline-secondary py-0 px-1" type="button"
                                        data-url="{% url 'loan_details_json' xl.id 'xmas' %}"
                                        onclick="fetchLoanDetails(this)"
                                        style="border: none; background: transparent; color: #0d6efd; font-size: 0.7rem;"
                                        data-bs-toggle="modal" data-bs-target="#loanDetailModal">
                                    <i class="fas fa-info-circle"></i>
                                </button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- ============================================= -->
        <!-- ===== MAIN LOANS TABLE (UPDATED with Details column) ===== -->
        <!-- ============================================= -->
        <div class="card-table">
            <div class="card-header">
                <span style="font-size: 0.75rem;"><i class="fas fa-layer-group me-1"></i> LOANS</span>
                <span class="badge-gold">{{ active_normal_count }} Active</span>
            </div>
            <div class="table-scroll">
                <table class="table align-middle mb-0">
                    <thead>
                        <tr>
                            <th class="ps-3" style="font-size: 0.55rem;">Loan Details</th>
                            <th style="font-size: 0.55rem;">Total Paid</th>
                            <th style="font-size: 0.55rem;">Balance</th>
                            <th style="font-size: 0.55rem;">Penalties</th>
                            <th class="text-center" style="font-size: 0.55rem;">Status</th>
                            <th class="text-center" style="font-size: 0.55rem;">Details</th> <!-- NEW -->
                        </tr>
                    </thead>
                    <tbody>
                        {% for l in loans %}
                        <tr>
                            <td class="ps-3">
                                <div style="font-weight: 700; color: var(--welfare-dark-green); font-size: 0.72rem;">{{ l.purpose }}</div>
                                <small class="text-muted" style="font-size: 0.55rem;">Applied: {{ l.application_date|date:"d M, Y" }}</small>
                            </td>
                            <td style="color: #28a745; font-weight: 700; font-size: 0.78rem;">KES {{ l.total_paid|floatformat:0 }}</td>
                            <td style="color: var(--welfare-maroon); font-weight: 700; font-size: 0.78rem;">KES {{ l.remaining_balance|floatformat:0 }}</td>
                            <td>
                                {% if l.penalty_due > 0 %}
                                <span style="color: #ffc107; font-weight: 700; font-size: 0.72rem;">KES {{ l.penalty_due|floatformat:0 }}</span>
                                {% else %}
                                <span class="text-muted" style="font-size: 0.6rem;">None</span>
                                {% endif %}
                            </td>
                            <td class="text-center">
                                <span class="badge-status {% if l.status == 'approved' or l.status == 'disbursed' %}approved{% elif l.status == 'pending_guarantors' %}pending{% else %}rejected{% endif %}">
                                    {{ l.get_status_display }}
                                </span>
                            </td>
                            <td class="text-center">
                                <button class="btn btn-sm btn-outline-secondary py-0 px-1" type="button"
                                        data-url="{% url 'loan_details_json' l.id 'normal' %}"
                                        onclick="fetchLoanDetails(this)"
                                        style="border: none; background: transparent; color: #0d6efd; font-size: 0.7rem;"
                                        data-bs-toggle="modal" data-bs-target="#loanDetailModal">
                                    <i class="fas fa-info-circle"></i>
                                </button>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="6" class="text-center py-3 text-muted" style="font-size: 0.75rem;">No loan records found.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ============================================= -->
        <!-- ===== RECENT SAVINGS & SHARES BREAKDOWN ===== -->
        <!-- ============================================= -->
        <div class="bottom-grid">
            <!-- Recent Savings -->
            <div class="card-table">
                <div class="card-header" style="font-size: 0.7rem;"><i class="fas fa-history me-1"></i> Recent Savings</div>
                <div class="card-body">
                    {% for s in savings|slice:":5" %}
                    <div class="saving-row">
                        <span class="date">{{ s.created_at|date:"d M, Y" }}</span>
                        <span class="amount">KES {{ s.amount|floatformat:0 }}</span>
                        <a href="{% url 'download_receipt' s.id %}" class="download"><i class="fas fa-download"></i></a>
                    </div>
                    {% empty %}
                    <div class="text-center py-2 text-muted" style="font-size: 0.7rem;">No recent savings recorded.</div>
                    {% endfor %}
                </div>
            </div>

            <!-- Shares Breakdown -->
            <div class="card-table">
                <div class="card-header" style="background: linear-gradient(135deg, var(--welfare-maroon), #4a0000); color: var(--welfare-gold); font-size: 0.7rem;">
                    <i class="fas fa-chart-pie me-1"></i> Shares Breakdown
                </div>
                <div class="card-body">
                    {% for sh in shares %}
                    <div class="share-row">
                        <span class="type">{{ sh.share_setting.share_type }}</span>
                        <span class="amount">KES {{ sh.amount|floatformat:0 }}</span>
                    </div>
                    {% empty %}
                    <div class="text-center py-2 text-muted" style="font-size: 0.7rem;">No share records found.</div>
                    {% endfor %}
                </div>
            </div>
        </div>

    </main>

    <!-- ============================================= -->
    <!-- ===== MODAL FOR LOAN DETAILS (NEW) ===== -->
    <!-- ============================================= -->
    <div class="modal fade" id="loanDetailModal" tabindex="-1" aria-labelledby="loanDetailModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header" style="background: linear-gradient(135deg, var(--welfare-dark-green), var(--welfare-maroon)); color: white;">
                    <h5 class="modal-title" id="loanDetailModalLabel">
                        <i class="fas fa-file-invoice me-2"></i> Loan Details
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="loanDetailBody">
                    <div class="text-center py-4">
                        <div class="spinner-border text-success" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2">Loading loan details...</p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>

    <!-- ============================================= -->
    <!-- ===== SCRIPTS ===== -->
    <!-- ============================================= -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js">
    </script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11">
    </script>

    <script>
        // =============================================
        // 1. MOBILE SIDEBAR TOGGLE
        // =============================================
        (function() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            const toggleBtn = document.getElementById('sidebarToggle');
            const mainContent = document.getElementById('mainContent');

            function openSidebar() {
                sidebar.classList.add('open');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }

            function closeSidebar() {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }

            function toggleSidebar() {
                if (sidebar.classList.contains('open')) {
                    closeSidebar();
                } else {
                    openSidebar();
                }
            }

            if (toggleBtn) {
                toggleBtn.addEventListener('click', toggleSidebar);
            }

            if (overlay) {
                overlay.addEventListener('click', closeSidebar);
            }

            // Close sidebar on escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && sidebar.classList.contains('open')) {
                    closeSidebar();
                }
            });

            // Close sidebar when a nav link is clicked (on mobile)
            sidebar.querySelectorAll('a').forEach(function(link) {
                link.addEventListener('click', function() {
                    if (window.innerWidth < 768) {
                        closeSidebar();
                    }
                });
            });

            // Handle resize: close sidebar on desktop
            let resizeTimer;
            window.addEventListener('resize', function() {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(function() {
                    if (window.innerWidth >= 768 && sidebar.classList.contains('open')) {
                        closeSidebar();
                    }
                }, 200);
            });
        })();

        // =============================================
        // 2. TOAST / SMS NOTIFICATION
        // =============================================
        function showSMSPopup(message, type) {
            type = type || 'success';
            const container = document.getElementById('toast-container');
            if (!container) return;

            const popup = document.createElement('div');
            popup.className = 'sms-popup ' + type;

            const iconMap = {
                success: 'fa-check-circle',
                danger: 'fa-exclamation-circle',
                info: 'fa-info-circle',
                warning: 'fa-exclamation-triangle'
            };
            const icon = iconMap[type] || 'fa-check-circle';

            popup.innerHTML = `
                    <div class="icon"><i class="fas ${icon}"></i></div>
                    <div class="msg">
                        <strong>ELDOPOLY WELFARE</strong>
                        <span>${message}</span>
                    </div>
                    <button class="close-btn" aria-label="Close notification"><i class="fas fa-times"></i></button>
                `;

            container.appendChild(popup);

            // Show with animation
            requestAnimationFrame(function() {
                popup.classList.add('show');
            });

            // Close button
            popup.querySelector('.close-btn').addEventListener('click', function() {
                popup.classList.remove('show');
                setTimeout(function() { popup.remove(); }, 400);
            });

            // Auto dismiss after 12 seconds
            setTimeout(function() {
                if (popup.parentElement) {
                    popup.classList.remove('show');
                    setTimeout(function() { popup.remove(); }, 400);
                }
            }, 12000);
        }

        // =============================================
        // 3. DJANGO MESSAGES → TOAST
        // =============================================
        document.addEventListener('DOMContentLoaded', function() {
            {% if messages %}
            {% for message in messages %}
            showSMSPopup("{{ message|escapejs }}", "{% if message.tags == 'error' %}danger{% elif message.tags == 'success' %}success{% else %}info{% endif %}");
            {% endfor %}
            {% endif %}
        });

        // =============================================
        // 4. UPDATE GOAL
        // =============================================
        function updateGoal(type) {
            type = type || 'saving';
            let currentValue = type === 'saving' ? "{{ profile.monthly_saving_target }}" : "{{ profile.share_goal }}";
            let title = type === 'saving' ? 'Monthly Saving Target' : 'Capital Share Goal';
            let minValue = type === 'share' ? 500 : 0;

            let goal = prompt('Enter new ' + title + ' (KES):', currentValue);
            if (goal === null) return;
            goal = parseFloat(goal);

            if (isNaN(goal) || goal < minValue) {
                showSMSPopup('Please enter a valid amount (Min KES ' + minValue + ' for shares).', 'danger');
                return;
            }

            showSMSPopup('Updating records...', 'info');

            fetch("{% url 'update_targets' %}", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": "{{ csrf_token }}",
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        saving_target: type === 'saving' ? goal : null,
                        share_goal: type === 'share' ? goal : null
                    })
                })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.status === 'success') {
                        showSMSPopup('Success! Your targets have been updated.', 'success');
                        setTimeout(function() { location.reload(); }, 1500);
                    } else {
                        showSMSPopup(data.message || 'Operation failed.', 'danger');
                    }
                })
                .catch(function(err) {
                    console.error('Fetch error:', err);
                    showSMSPopup('Network error. Could not connect to server.', 'danger');
                });
        }

        // =============================================
        // 5. PAY BEREAVEMENT
        // =============================================
        function payBereavement(bereavementId, deceasedName, amount) {
            Swal.fire({
                title: 'Monthly Bereavement Contribution',
                html: `
                        <div class="text-start">
                            <p><strong>Deceased:</strong> ${deceasedName}</p>
                            <p><strong>This month's amount:</strong> KES ${amount.toFixed(2)}</p>
                            <p class="text-muted small">You are paying the current month's instalment.</p>
                        </div>
                    `,
                icon: 'info',
                showCancelButton: true,
                confirmButtonColor: '#800000',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Pay Now',
                cancelButtonText: 'Cancel'
            }).then(function(result) {
                if (result.isConfirmed) {
                    window.location.href = '/pay-bereavement-mpesa/' + bereavementId + '/';
                }
            });
        }

        // =============================================
        // 6. PAY RETIREMENT
        // =============================================
        function payRetirement(announcementId, retireeName, amount) {
            Swal.fire({
                title: 'Retirement Contribution',
                html: `
                        <div class="text-start">
                            <p><strong>Retiree:</strong> ${retireeName}</p>
                            <p><strong>This month's amount:</strong> KES ${amount.toFixed(2)}</p>
                            <p class="text-muted small">You are paying the current month's retirement instalment.</p>
                        </div>
                    `,
                icon: 'info',
                showCancelButton: true,
                confirmButtonColor: '#004d26',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Pay Now',
                cancelButtonText: 'Cancel'
            }).then(function(result) {
                if (result.isConfirmed) {
                    window.location.href = '/pay-retirement-mpesa/' + announcementId + '/';
                }
            });
        }

        // =============================================
        // 7. COLLAPSE ICON ROTATION
        // =============================================
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(function(trigger) {
                trigger.addEventListener('click', function() {
                    var icon = this.querySelector('.collapse-icon');
                    if (icon) {
                        icon.classList.toggle('rotated');
                    }
                });
            });
        });

        // =============================================
        // 8. FETCH LOAN DETAILS (NEW)
        // =============================================
        function fetchLoanDetails(buttonElement) {
            const url = buttonElement.getAttribute('data-url');
            if (!url) {
                showSMSPopup('Error: No URL provided for loan details.', 'danger');
                return;
            }

            const modalBody = document.getElementById('loanDetailBody');
            modalBody.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-success" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading loan details...</p>
                </div>
            `;

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP error ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        modalBody.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                        return;
                    }

                    let html = `<div class="container-fluid">`;
                    html += `
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Loan ID:</strong> #${data.id}<br>
                                <strong>Amount:</strong> KES ${data.amount.toFixed(2)}<br>
                                <strong>Monthly Installment:</strong> KES ${data.monthly_installment.toFixed(2)}
                            </div>
                            <div class="col-md-6">
                                <strong>Total Paid:</strong> KES ${data.total_paid ? data.total_paid.toFixed(2) : '0.00'}<br>
                                <strong>Remaining Balance:</strong> KES ${data.remaining_balance.toFixed(2)}<br>
                                <strong>Status:</strong> <span class="badge bg-${data.status === 'approved' || data.status === 'disbursed' ? 'success' : data.status === 'rejected' ? 'danger' : 'warning'}">${data.status}</span>
                            </div>
                        </div>
                    `;

                    if (data.guarantors && data.guarantors.length > 0) {
                        html += `<div class="mb-3"><strong>Guarantors:</strong><ul class="list-unstyled">`;
                        data.guarantors.forEach(g => {
                            html += `<li>${g.name} – KES ${g.amount.toFixed(2)} (${g.status})</li>`;
                        });
                        html += `</ul></div>`;
                    } else {
                        html += `<div class="mb-3"><strong>Guarantors:</strong> <span class="text-muted">None</span></div>`;
                    }

                    if (data.schedules && data.schedules.length > 0) {
                        html += `<div><strong>Repayment Schedule</strong><div class="table-responsive mt-2">`;
                        html += `<table class="table table-sm table-bordered" style="font-size: 0.8rem;">`;
                        html += `<thead><tr><th>#</th><th>Due Date</th><th>Amount</th><th>Paid?</th><th>Date Paid</th></tr></thead><tbody>`;
                        data.schedules.forEach(s => {
                            const paidIcon = s.is_paid ? '<i class="fas fa-check-circle text-success"></i>' : '<i class="fas fa-times-circle text-danger"></i>';
                            html += `<tr>
                                <td>${s.installment}</td>
                                <td>${s.due_date}</td>
                                <td>KES ${s.amount_due.toFixed(2)}</td>
                                <td>${paidIcon}</td>
                                <td>${s.date_paid || '-'}</td>
                            </tr>`;
                        });
                        html += `</tbody></table></div></div>`;
                    } else {
                        html += `<div><strong>Repayment Schedule:</strong> <span class="text-muted">No schedule available</span></div>`;
                    }

                    html += `</div>`;
                    modalBody.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error fetching loan details:', error);
                    modalBody.innerHTML = `<div class="alert alert-danger">Failed to load loan details. Please try again.</div>`;
                    showSMSPopup('Could not load loan details. Please check your connection.', 'danger');
                });
        }
    </script>

</body>
</html>