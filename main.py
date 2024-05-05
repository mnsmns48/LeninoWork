import asyncio

from func import info


async def main():
    text = await info()
    print(text)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Script stopped')
