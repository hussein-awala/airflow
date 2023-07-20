# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from flask import request
from flask.sessions import SecureCookieSessionInterface
from flask_session.sessions import SqlAlchemySessionInterface


class SesssionExemptMixin:
    """Exempt certain blueprints/paths from autogenerated sessions."""

    def save_session(self, *args, **kwargs):
        """Prevent creating session from REST API and health requests."""
        if request.blueprint == "/api/v1":
            return None
        if request.path == "/health":
            return None
        return super().save_session(*args, **kwargs)


class AirflowDatabaseSessionInterface(SesssionExemptMixin, SqlAlchemySessionInterface):
    """Session interface that exempts some routes and stores session data in the database."""


class AirflowSecureCookieSessionInterface(SesssionExemptMixin, SecureCookieSessionInterface):
    """Session interface that exempts some routes and stores session data in a signed cookie."""
