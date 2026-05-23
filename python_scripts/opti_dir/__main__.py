from argparse import ArgumentParser, Namespace
from os import cpu_count
from os.path import basename
from pathlib import Path


from python_scripts.logger import Logger
from python_scripts.opti_dir import (
	EnvironmentArgument,
	Features,
	FeatureSets,
	InternalFeatures,
	optimize_directory
)


print("THIS IS OUTDATED. USE OPTI-DIR2!")


LOGGER: Logger = Logger("opti-dir")


def parse_args() -> Namespace:  # NOSONAR
	parser = ArgumentParser()
	parser.add_argument(
		"directory",
		type=str,
		default=".",
		action="store",
		nargs="?",
		help="where the images to be optimized are located"
	)
	parser.add_argument(
		"-t",
		"--threads",
		dest="threads",
		type=int,
		default=cpu_count() - 2,
		action="store",
		help="the amount of used threads. Defaults to [all - 2]"
	)
	parser.add_argument(
		"-f",
		"--features",
		dest="features",
		type=str,
		default="",
		action="store",
		help="comma separated list of features to enable. Available features: "
			 f"{", ".join([str(f) for f in Features])}"
	)
	parser.add_argument(
		"-s",
		"--feature-set",
		dest="feature_set",
		default=None,
		type=str,
		action="store",
		help="name of the feature set to enable. Available feature sets: "
			 f"{", ".join([str(fs) for fs in FeatureSets])}"
	)
	parser.add_argument(
		"--16",
		dest="use_16_bit",
		action="store_true",
		help="allow jpeg2png to create 16-bit png's (this will create massive png's!)"
	)
	parser.add_argument(
		"--list-env",
		dest="list_environment",
		action="store_true",
		help="list environment arguments and exit"
	)
	parser.add_argument("-d", "--dir-from-file", dest="use_dir", action="store_true", help="use the file's directory")
	parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="verbose logging")
	args = parser.parse_args()
	
	Logger.verbose_enabled = args.verbose
	
	args.directory = Path(args.directory).expanduser().resolve().absolute()
	
	if not args.directory.is_dir():
		if args.use_dir:
			LOGGER.verbose_log(f"resolving given file ({args.directory} -> {args.directory.parent})")
			args.directory = args.directory.parent
		else:
			LOGGER.error("the given directory is not a directory")
			exit(1)
	
	if args.threads < 1:
		LOGGER.warn("negative thread amount; using 1")
		args.threads = 1
	
	InternalFeatures.enable_through_args(args)
	Features.enable_trough_args(args)
	
	if args.feature_set is not None:
		FeatureSets.enable_feature_set(args.feature_set)
	
	if Features.JPEG_BETTER_DECODE.enabled:
		LOGGER.warn("jpeg2png enabled. This will increase file size of jpeg's!")
	
	if InternalFeatures.USE_16_BIT.enabled:
		LOGGER.warn("jpeg2png will create massive 16-bit png!")
	
	if len((enabled_features := Features.filter(True))) > 0:
		LOGGER.verbose_log(f"enabled features: {", ".join([str(f) for f in enabled_features])}")
	
	if args.list_environment:
		EnvironmentArgument.list_for_user()
		exit()
	
	if args.verbose:
		EnvironmentArgument.list_for_user()
		LOGGER.verbose_log(f"using {args.threads} threads for {basename(args.directory)}")
	
	return args


def main() -> None:
	args: Namespace = parse_args()
	optimize_directory(args.directory, args.threads)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("\rShutting down, this may take a while...")
