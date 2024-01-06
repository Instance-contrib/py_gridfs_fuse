import logging
import optparse
import llfuse

from gridfs_fuse.operations import operations_factory


def configure_optparse(parser):
    parser.add_option(
        '--mongodb-uri',
        dest='mongodb_uri',
        default="mongodb://127.0.0.1:27017",
        help="Connection string for MongoClient. http://goo.gl/abqY9")

    parser.add_option(
        '--database',
        dest='database',
        default='gridfs_fuse',
        help="Name of the database where the filesystem goes")

    parser.add_option(
        '--mount-point',
        dest='mount_point',
        help="Path where to mount fuse/gridfs wrapper")

    parser.add_option(
        '--log-level',
        dest='log_level',
        default='INFO',
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    return parser


def validate_options(options):
    if not options.mongodb_uri:
        raise Exception("--mongodb-uri is mandatory")

    if not options.database:
        raise Exception("--database is mandatory")

    if not options.mount_point:
        raise Exception("--mount-point is mandatory")

    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if options.log_level.upper() not in valid_log_levels:
        raise Exception(
            "--log-level must be one of " + ",".join(valid_log_levels)
        )


def run_fuse_mount(ops, options, mount_opts):
    mount_opts = ['fsname=gridfs_fuse'] + mount_opts
    llfuse.init(ops, options.mount_point, mount_opts)

    try:
        llfuse.main(workers=1)
    finally:
        llfuse.close()


def main():
    parser = optparse.OptionParser()
    configure_optparse(parser)
    options, args = parser.parse_args()
    validate_options(options)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, options.log_level.upper()))

    ops = operations_factory(options)

    # TODO: Still not sure which options to use
    # 'allow_other' Regardless who mounts it, all other users can access it
    # 'default_permissions' Let the kernel do the permission checks
    # 'nonempty' Allow mount on non empty directory
    mount_opts = ['default_permissions']

    run_fuse_mount(ops, options, mount_opts)


if __name__ == '__main__':
    main()
