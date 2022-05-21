# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2021 Frédéric Pierret (fepitre) <frederic@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

from qubesbuilder.component import QubesComponent
from qubesbuilder.distribution import QubesDistribution
from qubesbuilder.executors import Executor
from qubesbuilder.log import get_logger
from qubesbuilder.plugins import (
    DistributionPlugin,
    PluginError,
)

log = get_logger("source")


class SourceError(PluginError):
    pass


class SourcePlugin(DistributionPlugin):
    """
    Manage generic distribution source
    """

    def __init__(
        self,
        component: QubesComponent,
        dist: QubesDistribution,
        executor: Executor,
        plugins_dir: Path,
        artifacts_dir: Path,
        backend_vmm: str,
        verbose: bool = False,
        debug: bool = False,
        skip_if_exists: bool = False,
    ):
        super().__init__(
            component=component,
            dist=dist,
            plugins_dir=plugins_dir,
            artifacts_dir=artifacts_dir,
            verbose=verbose,
            debug=debug,
            backend_vmm=backend_vmm,
        )
        self.executor = executor
        self.skip_if_exists = skip_if_exists

        # Set and update parameters based on top-level "source",
        # per package set and per distribution.
        parameters = self.component.get_parameters(self._placeholders)

        self.parameters.update(parameters.get("source", {}))
        self.parameters.update(
            parameters.get(self.dist.package_set, {}).get("source", {})
        )
        self.parameters.update(
            parameters.get(self.dist.distribution, {}).get("source", {})
        )

    def run(self, stage: str):
        # Compare previous artifacts hash with current source hash
        fetch_info = self.get_artifacts_info("fetch", "source")

        if stage == "prep":
            # Compare previous artifacts hash with current source hash
            if not fetch_info.get("source-hash"):
                raise SourceError(
                    f"{self.component}:{self.dist}: Missing 'fetch' stage artifacts!"
                )
