from __future__ import annotations

from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
)
from apmodel import Activity
from fastapi.params import Depends
from fastapi import APIRouter, Request, Response
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute
from starlette.types import ASGIApp, Lifespan

from ..client.models import Resource as WebfingerResource
from .types import Context
from ..types import Outbox


class SubRouter(APIRouter):
    def __init__(
        self,
        *,
        prefix: str = "",
        tags: List[str | Enum] | None = None,
        dependencies: Sequence[Depends] | None = None,
        default_response_class: type[Response] = JSONResponse,
        responses: Dict[int | str, Dict[str, Any]] | None = None,
        callbacks: List[BaseRoute] | None = None,
        routes: List[BaseRoute] | None = None,
        redirect_slashes: bool = True,
        default: Optional[ASGIApp] = None,
        dependency_overrides_provider: Any | None = None,
        route_class: type[APIRoute] = APIRoute,
        on_startup: Sequence[Callable[[], Any]] | None = None,
        on_shutdown: Sequence[Callable[[], Any]] | None = None,
        lifespan: Optional[Lifespan[Any]] = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[APIRoute], str] = generate_unique_id,
    ) -> None:
        self._ap_events = {}
        self._ap_outbox: Optional[Callable[[Context], Awaitable[Any]]] = None
        self._ap_webfinger_route: Optional[
            Callable[[Request, WebfingerResource], Awaitable[Any]]
        ] = None
        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
        )

    def on(
        self,
        type: Union[type[Activity], type[Outbox]],
        func: Optional[Callable] = None,
    ):
        def decorator(func: Callable) -> Callable:
            if type == Activity:
                self._ap_events[type] = func
            elif type == Outbox:
                self._ap_outbox = func
            return func

        if func is not None:
            return decorator(func)

        return decorator

    def webfinger(self, func: Optional[Callable] = None):
        def decorator(func: Callable) -> Callable:
            self._ap_webfinger_route = func
            return func

        if func is not None:
            return decorator(func)

        return decorator

    def nodeinfo(
        self,
        route: str,
        version: Literal["2.0", "2.1"],
        func: Optional[Callable] = None,
    ) -> Callable:
        """Define Nodeinfo route.

        Args:
            route (str): route path.
            version (Literal[&quot;2.0&quot;, &quot;2.1&quot;]): nodeinfo version
            func (Optional[FunctionType], optional): If use that as decorator, ignore this. Defaults to None.

        Returns:
            Union[None, Callable]: no description
        """

        def decorator(fn: Callable) -> Callable:
            if version == "2.0":
                self.add_api_route(
                    path=route,
                    endpoint=fn,
                    methods=["GET"],
                    name="__apkit_nodeinfo_2.0",
                    include_in_schema=False,
                )
            elif version == "2.1":
                self.add_api_route(
                    path=route,
                    endpoint=fn,
                    methods=["GET"],
                    name="__apkit_nodeinfo_2.1",
                    include_in_schema=False,
                )
            return fn

        if func is not None:
            return decorator(func)

        return decorator

    def include_router(
        self,
        router: APIRouter | SubRouter,
        *,
        prefix: str = "",
        tags: List[str | Enum] | None = None,
        dependencies: Sequence[Depends] | None = None,
        default_response_class: type[Response] = JSONResponse,
        responses: Dict[int | str, Dict[str, Any]] | None = None,
        callbacks: List[BaseRoute] | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[APIRoute], str] = generate_unique_id,
    ) -> None:
        super().include_router(
            router,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
        )
        if isinstance(router, SubRouter):
            self._ap_events = {**router._ap_events, **self._ap_events}
            self._ap_outbox = (
                self._ap_outbox if not router._ap_outbox else router._ap_outbox
            )
            self._ap_webfinger_route = (
                self._ap_webfinger_route
                if not router._ap_webfinger_route
                else router._ap_webfinger_route
            )
