from argparse import Namespace
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from python_scripts.logger import Logger
from python_scripts.opti_dir.executable import Executable, Executables

__all__ = ["Feature", "Features", "InternalFeatures", "FeatureSet", "FeatureSets"]


LOGGER: Logger = Logger("opti-dir")


@dataclass
class Feature:
	name_: str  # name is used by Enum
	display_name: str
	requirement: Executable | None = None
	enabled: bool = field(init=False, default=False)
	
	def enable(self) -> None:
		if self.requirement is not None and not self.requirement.available:
			LOGGER.error(f"Feature {self.display_name} requires {self.requirement.binary}, but it is not available")
			exit(1)
		
		self.enabled = True
	
	def should_run_on(self, image: Path) -> bool:
		"""
		Whether this feature should run on the given image. This is essentially a bigger enabled check.
		:param image: The image, to maybe run on
		:return: ``True``, if this feature is enabled *AND* the given image matches the filter
		"""
		return self.enabled and self.requirement.filter(image)
	
	def __eq__(self, other):
		if isinstance(other, Feature):
			return self.name_ == other.name_
		if isinstance(other, str):
			return self.name_ == other
		return False
	
	def __str__(self) -> str:
		return f"{self.name_} ({self.display_name})"


class Features(Feature, Enum):
	JXL_ENCODE = "cjxl", "encode to JXL", Executables.CJXL
	DELETE_ORIGINAL = "rm", "remove original"
	JPEG_BETTER_DECODE = "j2p", "better jpeg decoding", Executables.JPEG2PNG
	FIX_IMAGES = "fix", "try to fix bad image extensions"
	WEBP_DECODE = "dwebp", "decode webp images", Executables.DWEBP
	
	@classmethod
	def get(cls, name: str) -> Feature | None:
		for f in cls:
			if f.name_ == name:
				return f
		return None
	
	@classmethod
	def filter(cls, enabled: bool) -> list[Feature]:
		return list(filter(lambda f: f.enabled == enabled, cls))
	
	# fuck python
	def __str__(self):
		return str(self.value)
	
	@classmethod
	def enable_trough_args(cls, args: Namespace) -> None:
		bad_feature: bool = False
		for feature in args.features.split(","):
			if (f := cls.get(feature)) is not None:
				f.enable()
			else:
				if feature != "":
					LOGGER.error(f"Given feature '{feature}' does not exist!")
					bad_feature = True
		
		if bad_feature:
			exit(1)


@dataclass
class FeatureSet:
	name_: str
	description: str
	features: list[Feature]
	
	def _enable_set(self) -> None:
		for feature in self.features:
			feature.enable()
	
	def __str__(self) -> str:
		return f"{self.name_} ({self.description}: {",".join([f.name_ for f in self.features])})"


class FeatureSets(FeatureSet, Enum):
	ALL = "all", "enable all features", [f for f in Features]
	GENERAL_PICTURE = "general", "general image improvements", [
		Features.DELETE_ORIGINAL, Features.JPEG_BETTER_DECODE, Features.FIX_IMAGES, Features.WEBP_DECODE
	]
	safe = "safe", "general, non-destructive image improvements", [Features.FIX_IMAGES]
	
	def __str__(self) -> str:
		return str(self.value)
	
	@classmethod
	def get(cls, name: str) -> FeatureSet | None:
		for feature_set in cls:
			if feature_set.name_ == name:
				return feature_set
		
		return None
	
	@classmethod
	def enable_feature_set(cls, feature_set_name: str) -> None:
		if (feature_set := FeatureSets.get(feature_set_name)) is not None:
			feature_set._enable_set()
		else:
			LOGGER.error(f"Given feature set '{feature_set}' does not exist!")
			exit(1)


class InternalFeatures(Feature, Enum):
	USE_16_BIT = "16-bit", "if 16-bit colour depth should be used"
	
	@classmethod
	def enable_through_args(cls, args: Namespace) -> None:
		if args.use_16_bit:
			cls.USE_16_BIT.enable()
	
	def __str__(self) -> str:
		return str(self.value)
