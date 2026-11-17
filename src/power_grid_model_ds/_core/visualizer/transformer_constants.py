# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Shared transformer rendering identifiers and symbol dimensions."""

TRANSFORMER_GROUP = "transformer"
TRANSFORMER_SYMBOL_GROUP = "transformer_symbol"
TRANSFORMER_SYMBOL_CLASS = "transformer-symbol"
TRANSFORMER_HIDDEN_CLASS = "transformer-original-hidden"
TRANSFORMER_CONNECTION_CLASS = "transformer-visual-connection"
TRANSFORMER_OPEN_CLASS = "transformer-visual-open"
TRANSFORMER_OPEN_FROM_CLASS = "transformer-visual-open-from"
TRANSFORMER_OPEN_TO_CLASS = "transformer-visual-open-to"
VISUAL_ONLY_KEY = "visual_only"
TRANSFORMER_VISUAL_PREFIX = "__visual_transformer__"
TRANSFORMER_SYMBOL_SUFFIX = "__symbol"
TRANSFORMER_FROM_SUFFIX = "__from"
TRANSFORMER_TO_SUFFIX = "__to"

TRANSFORMER_SYMBOL_LENGTH = 132
TRANSFORMER_CIRCLE_RADIUS = 33
TRANSFORMER_CIRCLE_OFFSET = 18
TRANSFORMER_STROKE_WIDTH = 10
TRANSFORMER_SYMBOL_MARGIN = 8
MIN_TRANSFORMER_CONNECTION_LENGTH = TRANSFORMER_SYMBOL_LENGTH

# A browser-side Cytoscape position listener keeps symbols aligned during dragging.
LOCK_TRANSFORMER_ENDPOINTS = False
