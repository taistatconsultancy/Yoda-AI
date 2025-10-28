#!/usr/bin/env python3
"""
Check for null bytes in timezone_utils.py
"""
def check_null_bytes():
    with open('app/services/timezone_utils.py', 'rb') as f:
        content = f.read()
        print(f'File size: {len(content)} bytes')
        
        null_bytes = b'\x00'
        count = content.count(null_bytes)
        print(f'Null bytes found: {count}')
        
        if null_bytes in content:
            print('⚠️ File contains null bytes!')
            # Show where null bytes are
            for i, byte in enumerate(content):
                if byte == 0:
                    print(f'Null byte at position {i}')
        else:
            print('✅ No null bytes found')
            
        # Show content preview
        print(f'Content preview: {content[:200]}')

if __name__ == "__main__":
    check_null_bytes()
