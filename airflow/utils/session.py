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

import contextlib
from functools import wraps
from inspect import signature
from typing import Callable, Generator, TypeVar, cast

from sqlalchemy.ext.asyncio import AsyncSession as ASAsyncSession
from sqlalchemy.orm import Session as SASession

from airflow import settings
from airflow.typing_compat import ParamSpec


@contextlib.contextmanager
def create_session() -> Generator[SASession, None, None]:
    """Contextmanager that will create and teardown a session."""
    Session = getattr(settings, "Session", None)
    if Session is None:
        raise RuntimeError("Session must be set before!")
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextlib.asynccontextmanager
async def create_async_session() -> Generator[ASAsyncSession, None, None]:
    """Contextmanager that will create and teardown an async session."""
    AsyncSession = getattr(settings, "AsyncSession", None)
    if AsyncSession is None:
        raise RuntimeError("AsyncSession must be set before!")
    async_session = AsyncSession()
    try:
        yield async_session
        await async_session.commit()
    except Exception:
        await async_session.rollback()
        raise
    finally:
        await async_session.close()


PS = ParamSpec("PS")
RT = TypeVar("RT")


def find_session_idx(func: Callable[PS, RT]) -> int:
    """Find session index in function call parameter."""
    func_params = signature(func).parameters
    try:
        # func_params is an ordered dict -- this is the "recommended" way of getting the position
        session_args_idx = tuple(func_params).index("session")
    except ValueError:
        raise ValueError(f"Function {func.__qualname__} has no `session` argument") from None

    return session_args_idx


def provide_session(func: Callable[PS, RT]) -> Callable[PS, RT]:
    """
    Provide a session if it isn't provided.

    If you want to reuse a session or run the function as part of a
    database transaction, you pass it to the function, if not this wrapper
    will create one and close it for you.
    """
    session_args_idx = find_session_idx(func)

    @wraps(func)
    def wrapper(*args, **kwargs) -> RT:
        if "session" in kwargs or session_args_idx < len(args):
            return func(*args, **kwargs)
        else:
            with create_session() as session:
                return func(*args, session=session, **kwargs)

    return wrapper


def provide_async_session(func: Callable[PS, RT]) -> Callable[PS, RT]:
    """
    Provide an async session if it isn't provided.

    If you want to reuse a session or run the function as part of a
    database transaction, you pass it to the function, if not this wrapper
    will create one and close it for you.
    """
    session_args_idx = find_session_idx(func)

    @wraps(func)
    async def wrapper(*args, **kwargs) -> RT:
        if "async_session" in kwargs or session_args_idx < len(args):
            yield func(*args, **kwargs)
        else:
            with await create_async_session() as session:
                yield func(*args, session=session, **kwargs)

    return wrapper


# A fake session to use in functions decorated by provide_session. This allows
# the 'session' argument to be of type Session instead of Session | None,
# making it easier to type hint the function body without dealing with the None
# case that can never happen at runtime.
NEW_SESSION: SASession = cast(SASession, None)
NEW_ASYNC_SESSION: ASAsyncSession = cast(ASAsyncSession, None)
