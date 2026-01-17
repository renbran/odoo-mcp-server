# -*- coding: utf-8 -*-
"""
Commission Models Initialization
==========================================================
Clean import order without circular dependencies
"""

import logging
_logger = logging.getLogger(__name__)

# Core models - load in dependency order
from . import commission_type
from . import commission_line
from . import commission_dashboard
from . import commission_report_generator

# Integration models
from . import sale_order
from . import purchase_order
from . import res_partner

# Deal tracking extensions (must load after sale_order)
from . import sale_order_deal_tracking_ext
from . import account_move_deal_tracking_ext

# Optional/Advanced models - load last to avoid circular imports
try:
    from . import commission_ai_analytics
    _logger.info("✅ commission_ai_analytics loaded")
except ImportError as e:
    _logger.info(f"⚠️  commission_ai_analytics not available: {e}")
