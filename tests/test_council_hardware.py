# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import pytest

from omega.council.models import HardwareProfile, ExecutionMode
from omega.council.execution_mode import select_execution_mode
from omega.council.hardware_detector import detect_hardware_profile


class TestCouncilHardwareAdaptation:
    def test_execution_mode_cloud_equivalent(self):
        mode = select_execution_mode(HardwareProfile.CLOUD_EQUIVALENT, node_count=10)
        assert mode == ExecutionMode.PARALLEL

    def test_execution_mode_local_32gb_dual(self):
        # 8 or fewer nodes can run in a single BATCH_8 sweep
        assert select_execution_mode(HardwareProfile.LOCAL_32GB_DUAL, node_count=8) == ExecutionMode.BATCH_8
        assert select_execution_mode(HardwareProfile.LOCAL_32GB_DUAL, node_count=6) == ExecutionMode.BATCH_8
        # More than 8 nodes split into BATCH_4 chunks
        assert select_execution_mode(HardwareProfile.LOCAL_32GB_DUAL, node_count=10) == ExecutionMode.BATCH_4

    def test_execution_mode_local_16gb(self):
        assert select_execution_mode(HardwareProfile.LOCAL_16GB, node_count=4) == ExecutionMode.BATCH_4
        assert select_execution_mode(HardwareProfile.LOCAL_16GB, node_count=5) == ExecutionMode.SERIAL_INDEPENDENT

    def test_execution_mode_local_8gb_and_4gb(self):
        assert select_execution_mode(HardwareProfile.LOCAL_8GB, node_count=4) == ExecutionMode.BATCH_2
        assert select_execution_mode(HardwareProfile.LOCAL_4GB, node_count=4) == ExecutionMode.SERIAL_INDEPENDENT

    def test_detector_with_custom_yaml(self, tmp_path: Path):
        # Test 32GB Dual Channel without discrete GPU -> LOCAL_32GB_DUAL
        yaml_32gb = tmp_path / "profile_32gb.yaml"
        yaml_32gb.write_text(
            "memory:\n"
            "  total_mb: 32768\n"
            "  channels: 2\n"
            "gpu:\n"
            "  vendor: intel\n"
            "  is_discrete: false\n"
        )
        assert detect_hardware_profile(yaml_32gb) == HardwareProfile.LOCAL_32GB_DUAL

        # Test 32GB with discrete GPU -> CLOUD_EQUIVALENT
        yaml_gpu = tmp_path / "profile_gpu.yaml"
        yaml_gpu.write_text(
            "memory:\n"
            "  total_mb: 32768\n"
            "gpu:\n"
            "  vendor: nvidia\n"
            "  is_discrete: true\n"
        )
        assert detect_hardware_profile(yaml_gpu) == HardwareProfile.CLOUD_EQUIVALENT

        # Test 16GB Profile -> LOCAL_16GB
        yaml_16gb = tmp_path / "profile_16gb.yaml"
        yaml_16gb.write_text(
            "memory:\n"
            "  total_mb: 16384\n"
        )
        assert detect_hardware_profile(yaml_16gb) == HardwareProfile.LOCAL_16GB

        # Test 8GB Profile -> LOCAL_8GB
        yaml_8gb = tmp_path / "profile_8gb.yaml"
        yaml_8gb.write_text(
            "memory:\n"
            "  total_mb: 8192\n"
        )
        assert detect_hardware_profile(yaml_8gb) == HardwareProfile.LOCAL_8GB

        # Test 32GB Single Channel -> LOCAL_16GB (not LOCAL_32GB_DUAL)
        # This is the critical bug fix: single-channel 32GB must not get BATCH_8
        yaml_32gb_single = tmp_path / "profile_32gb_single.yaml"
        yaml_32gb_single.write_text(
            "memory:\n"
            "  total_mb: 32768\n"
            "  channels: 1\n"
            "gpu:\n"
            "  vendor: intel\n"
            "  is_discrete: false\n"
        )
        assert detect_hardware_profile(yaml_32gb_single) == HardwareProfile.LOCAL_16GB
