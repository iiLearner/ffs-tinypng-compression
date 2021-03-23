import sys
import tinify
import dotenv
import os
from pathlib import Path
import asyncio

# load env
dotenv.load_dotenv()

# tiny_png auth
tinify.key = os.getenv("TINYFY_API_KEY")

# what types of files are we going to optimize
extensions = ['*.png', '*.jpeg']


async def optimize(image_path: str):
    source = tinify.from_file(image_path)
    source.to_file(image_path)


async def lookUp(path):
    totalCount = 0
    extensionCount = [0] * len(extensions)
    found_extensions = ""
    files = []
    for i, extension in enumerate(extensions):
        for file_path in Path(path).rglob(extension):
            totalCount += 1
            extensionCount[i] += 1
            files.append(file_path)

    for i, extension in enumerate(extensions):
        found_extensions += f"{extension}: {extensionCount[i]} | "

    return totalCount, found_extensions, files


async def main():
    path = input("Specify the folder path: ")
    if not os.path.exists(path):
        print("Specified path does not exist! please try again...\n")
        await main()

    print(f"Looking up '{path}' for {extensions}...")
    totalCount, found_extensions, files = await lookUp(path)
    print(f"Look up complete! Found a total of {totalCount} files. | {found_extensions[:-2].replace('*.', '')}")

    print(f"\nStarting compression..")
    for i, file_path in enumerate(files):
        sys.stdout.write(f"\rCompressed {i} of {totalCount} images | {round(i / totalCount * 100, 2)}%")
        await optimize(file_path)

    sys.stdout.write(f"\rCompressed {totalCount} of {totalCount} images | 100%")
    sys.stdout.flush()
    print("\nCompression completed successfully!")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
