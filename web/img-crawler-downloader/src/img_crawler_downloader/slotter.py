#!/usr/bin/env python3
# python3 -m pip install -U {packages-to-install}
# Run:
# python crawler-puller.py
import errno
import json
import os
import time

PATH_IMAGES = os.path.join("downloaded", "images")


def slotArchs():
    arch_infos: dict = json.load(open("downloaded/collection/archs.json"))
    print(arch_infos)
    for arch_info in arch_infos["archs"]:
        print(arch_info)
        slotImages(arch_info, "categories")
        slotImages(arch_info, "products")


def slotImages(arch_info, label_field):
    labels = arch_info[label_field]
    for label in labels:
        label_location = os.path.join(os.path.join("downloaded", label_field), label)
        os.makedirs(label_location, exist_ok=True)
        img_name = os.path.basename(arch_info["thumbnail"])
        img_link_name = os.path.join(label_location, img_name)
        if not os.path.exists(img_link_name):
            img_path = os.path.join(PATH_IMAGES, img_name)
            try:
                os.symlink(img_path, img_link_name)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    os.remove(img_link_name)
                    os.symlink(img_path, img_link_name)
                else:
                    raise e


def main():
    startTime = time.time()
    slotArchs()
    endTime = time.time()
    print(f"Total Time:{endTime - startTime}")


if __name__ == "__main__":
    exit(main())
