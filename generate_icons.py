#!/usr/bin/env python3
"""
Generate custom PNG icons for the sidebar
"""

from PIL import Image, ImageDraw
import os

def create_icon_base(size=24, bg_color=(37, 37, 37, 0)):
    """Create a base icon with transparent background"""
    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    return img, draw

def create_explorer_icon(size=24):
    """Create a file explorer icon"""
    img, draw = create_icon_base(size)
    
    # Colors for VS Code theme
    folder_color = (220, 220, 220, 255)  # Light gray
    
    # Draw folder icon
    # Folder back
    draw.rectangle([2, 6, size-2, size-2], fill=folder_color)
    # Folder tab
    draw.rectangle([2, 4, 10, 8], fill=folder_color)
    # Folder outline
    draw.rectangle([2, 6, size-2, size-2], outline=(180, 180, 180, 255), width=1)
    
    return img

def create_search_icon(size=24):
    """Create a search icon"""
    img, draw = create_icon_base(size)
    
    # Colors for VS Code theme
    search_color = (220, 220, 220, 255)  # Light gray
    
    # Draw magnifying glass
    center_x, center_y = size//2 - 2, size//2 - 2
    radius = 6
    
    # Draw circle (magnifying glass lens)
    draw.ellipse([center_x-radius, center_y-radius, center_x+radius, center_y+radius], 
                outline=search_color, width=2)
    
    # Draw handle
    handle_start_x = center_x + radius - 2
    handle_start_y = center_y + radius - 2
    handle_end_x = handle_start_x + 4
    handle_end_y = handle_start_y + 4
    
    draw.line([handle_start_x, handle_start_y, handle_end_x, handle_end_y], 
              fill=search_color, width=2)
    
    return img

def create_debug_icon(size=24):
    """Create a debug icon"""
    img, draw = create_icon_base(size)
    
    # Colors for VS Code theme
    debug_color = (220, 220, 220, 255)  # Light gray
    
    # Draw play button (triangle)
    points = [
        (6, 4),
        (6, size-4),
        (size-6, size//2)
    ]
    draw.polygon(points, fill=debug_color)
    
    # Draw small circle for breakpoint
    draw.ellipse([size-8, 4, size-4, 8], fill=(220, 50, 50, 255))
    
    return img

def create_extensions_icon(size=24):
    """Create an extensions icon"""
    img, draw = create_icon_base(size)
    
    # Colors for VS Code theme
    ext_color = (220, 220, 220, 255)  # Light gray
    
    # Draw puzzle piece-like shape
    # Main square
    draw.rectangle([4, 4, size-4, size-4], outline=ext_color, width=2)
    
    # Small squares (extensions)
    draw.rectangle([2, 8, 4, 12], fill=ext_color)
    draw.rectangle([size-4, 8, size-2, 12], fill=ext_color)
    draw.rectangle([8, 2, 12, 4], fill=ext_color)
    draw.rectangle([8, size-4, 12, size-2], fill=ext_color)
    
    return img

def create_settings_icon(size=24):
    """Create a settings/gear icon"""
    img, draw = create_icon_base(size)
    
    # Colors for VS Code theme
    gear_color = (220, 220, 220, 255)  # Light gray
    
    center = size // 2
    outer_radius = 8
    inner_radius = 4
    
    # Draw gear teeth (simplified)
    for i in range(8):
        angle = i * 45
        import math
        x1 = center + outer_radius * math.cos(math.radians(angle))
        y1 = center + outer_radius * math.sin(math.radians(angle))
        x2 = center + (outer_radius + 2) * math.cos(math.radians(angle))
        y2 = center + (outer_radius + 2) * math.sin(math.radians(angle))
        draw.line([x1, y1, x2, y2], fill=gear_color, width=2)
    
    # Draw outer circle
    draw.ellipse([center-outer_radius, center-outer_radius, 
                 center+outer_radius, center+outer_radius], 
                outline=gear_color, width=2)
    
    # Draw inner circle
    draw.ellipse([center-inner_radius, center-inner_radius, 
                 center+inner_radius, center+inner_radius], 
                outline=gear_color, width=2)
    
    return img

def main():
    """Generate all icons"""
    icons_dir = "resources/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    # Generate icons
    icons = {
        "explorer": create_explorer_icon(),
        "search": create_search_icon(),
        "debug": create_debug_icon(),
        "extensions": create_extensions_icon(),
        "settings": create_settings_icon()
    }
    
    # Save icons
    for name, icon in icons.items():
        icon.save(os.path.join(icons_dir, f"{name}.png"))
        print(f"Generated {name}.png")
    
    print("All icons generated successfully!")

if __name__ == "__main__":
    main()
