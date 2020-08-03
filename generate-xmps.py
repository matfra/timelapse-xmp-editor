#!/usr/bin/env python3

"""A xmp file duplicator / interpolator / generator for Adobe Camera Raw that does not even understand XMP!
"""

import os
import argparse
import glob


parser = argparse.ArgumentParser(
    description="Generate xmp files for developing many photos with similar or gradual settings from 2 DNG files"
)
parser.add_argument(
    "directory",
    type=str,
    help="working directory containing RAW pictures and the 2 edited extremities DNG files",
)
parser.add_argument(
    "pics_extension", type=str, help="Extension of the RAW pictures. Default : ARW"
)


def get_filespath_in_dir_with_extension(directory, extension):
    results = glob.glob(os.path.join(directory, "*.{}".format(extension)))
    results.sort()
    return results


def write_xmp_file(xmp, outfile_path):
    print("Writing file: {}".format(outfile_path))
    # if os.path.exists(outfile_path):
    #     raise FileExistsError("Not overwriting existing file {}".format(outfile_path))
    with open(outfile_path, "w") as outfile:
        for line in xmp:
            outfile.write(line)


def read_file_to_list_of_lines(file):
    with open(file, "r") as f:
        return f.readlines()


def read_kv_from_line(line):
    """Takes a line like and returns a tuple with float or str values:
    '   crs:Exposure2012="-1.00"\n' => ('Exposure2012', -1.0000)"""
    try:
        key, raw_value = line.split(":")[1].split("=")
        value = float(raw_value.split('"')[1])
    except ValueError:
        return None, None
    return key, value


def build_diff_keys(first_xmp, last_xmp):
    """Returns a dict containing the keys to interpolate"""
    result = {}
    first_xmp_values = {}
    last_xmp_values = {}
    for line in first_xmp:
        if line in last_xmp:
            continue
        first_xmp_key, first_xmp_value = read_kv_from_line(line)
        if first_xmp_value is None:
            continue
        first_xmp_values[first_xmp_key] = first_xmp_value

        for last_xmp_line in last_xmp:
            if first_xmp_key in last_xmp_line:
                last_xmp_key, last_xmp_value = read_kv_from_line(last_xmp_line)
                if last_xmp_value is None:
                    continue
                last_xmp_values[last_xmp_key] = last_xmp_value

    for first_xmp_key, first_xmp_value in first_xmp_values.items():
        if (
            first_xmp_key in last_xmp_values
            or isinstance(first_xmp_value, float) is False
        ):
            result[first_xmp_key] = (first_xmp_value, last_xmp_values[first_xmp_key])
    return result


def build_final_xmp(base_xmp, modified_keys, pics_count, pic_index):
    final_xmp = []
    for line in base_xmp:
        if "xmp:" in line:
            continue
        if "xmpMM:" in line:
            continue
        if "exif:" in line:
            continue
        if "photoshop:" in line:
            continue
        if "crs:" in line:
            key, value = read_kv_from_line(line)
            if key in modified_keys and value is not None:
                values = modified_keys[key]
                interpolated_value = values[0] + (
                    (pic_index + 1) * (values[1] - values[0]) / pics_count
                )
                interpolated_line = '   crs:{}="{}"\n'.format(key, interpolated_value)
                final_xmp.append(interpolated_line)
            else:
                final_xmp.append(line)
        else:
            final_xmp.append(line)
    return final_xmp


def main(args):
    xmps_paths = get_filespath_in_dir_with_extension(args.directory, "xmp")
    if len(xmps_paths) == 0:
        raise FileNotFoundError(
            "Could not find any xmp files in {}".format(args.directory)
        )
    first_xmp = read_file_to_list_of_lines(xmps_paths[0])
    last_xmp = read_file_to_list_of_lines(xmps_paths[-1])

    pics_paths = get_filespath_in_dir_with_extension(
        args.directory, args.pics_extension
    )
    pics_count = len(pics_paths)
    print("Found {} pictures".format(pics_count))

    modified_keys = build_diff_keys(first_xmp, last_xmp)

    pic_index = 0
    for pic_path in pics_paths:
        pic_index = pic_index + 1
        new_xmp_filename = ".".join([os.path.splitext(pic_path)[0], "xmp"])
        if new_xmp_filename == xmps_paths[0]:
            # Do not overwrite the first xmp file but do regenerate the last one so that duplciated settings can be applied there too
            continue
        new_xmp_content = build_final_xmp(
            first_xmp, modified_keys, pics_count, pic_index
        )
        write_xmp_file(new_xmp_content, new_xmp_filename)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
