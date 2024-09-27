import math

# Calculate flush volume based on color data
class FlushVolCalculator:  
    def __init__(self, min_flush_vol, max_flush_vol, multiplier):
        """
        min_flush_vol: Minimum flush volume
        max_flush_vol: Maximum flush volume
        multiplier: Flush multiplier
        """
        self.m_min_flush_vol = min_flush_vol  
        self.m_max_flush_vol = max_flush_vol  
        self.m_multiplier = multiplier
    
    def calc_flush_vol_by_rgb(self, src_r, src_g, src_b, dst_r, dst_g, dst_b):
        # Convert using the RGB model
  
        src_r_f = src_r / 255.0
        src_g_f = src_g / 255.0
        src_b_f = src_b / 255.0
        dst_r_f = dst_r / 255.0
        dst_g_f = dst_g / 255.0
        dst_b_f = dst_b / 255.0
  
        # Calculate color distance in the HSV color space  
        from_hsv_h, from_hsv_s, from_hsv_v = FlushVolCalculator.RGB2HSV(src_r_f, src_g_f, src_b_f)  
        to_hsv_h, to_hsv_s, to_hsv_v = FlushVolCalculator.RGB2HSV(dst_r_f, dst_g_f, dst_b_f)  
        hs_dist = FlushVolCalculator.DeltaHS_BBS(from_hsv_h, from_hsv_s, from_hsv_v, to_hsv_h, to_hsv_s, to_hsv_v)  
  
        # 1. If the target color has higher brightness, the color difference is more noticeable  
        # 2. If the source color has lower brightness, the color difference is more noticeable  
        from_lumi = FlushVolCalculator.get_luminance(src_r_f, src_g_f, src_b_f)  
        to_lumi = FlushVolCalculator.get_luminance(dst_r_f, dst_g_f, dst_b_f)
        lumi_flush = 0.0
        if to_lumi >= from_lumi:  
            lumi_flush = math.pow(to_lumi - from_lumi, 0.7) * 560.0
        else:  
            lumi_flush = (from_lumi - to_lumi) * 80.0
  
            inter_hsv_v = 0.67 * to_hsv_v + 0.33 * from_hsv_v  
            hs_dist = min(inter_hsv_v, hs_dist)  
  
        hs_flush = 230.0 * hs_dist  
  
        flush_volume = FlushVolCalculator.calc_triangle_3rd_edge(hs_flush, lumi_flush, 120.0)  
        #flush_volume = max(flush_volume, 60.0)  
        flush_volume = max(flush_volume, 0.0) # Limit the minimum volume
    
        flush_volume += self.m_min_flush_vol
        flush_volume *= self.m_multiplier
        flush_volume = min(int(flush_volume), self.m_max_flush_vol)
  
        return flush_volume
    
    def calc_flush_vol_by_hex(self, src_clr, dst_clr):
        """
        Calculate using hex format, e.g., "#C0C0C0"
        src_clr: Source color
        dst_clr: Target color
        """
        return self.calc_flush_vol_by_rgb(*FlushVolCalculator.hex_to_rgb(src_clr), *FlushVolCalculator.hex_to_rgb(dst_clr))
    
    @staticmethod
    def RGB2HSV(r, g, b):  
        Cmax = max(r, g, b)  
        Cmin = min(r, g, b)  
        delta = Cmax - Cmin  
    
        if abs(delta) < 0.001:  
            h = 0.0  
        elif Cmax == r:  
            h = 60.0 * math.fmod((g - b) / delta, 6.0)  
        elif Cmax == g:  
            h = 60.0 * ((b - r) / delta + 2)  
        else:  
            h = 60.0 * ((r - g) / delta + 4)  
    
        if abs(Cmax) < 0.001:  
            s = 0.0  
        else:  
            s = delta / Cmax  
    
        v = Cmax  
    
        return h, s, v 

    @staticmethod
    def to_radians(degree):  
        return degree / 180.0 * math.pi  
    
    @staticmethod
    def get_luminance(r, g, b):  
        return r * 0.3 + g * 0.59 + b * 0.11  
    
    @staticmethod
    def calc_triangle_3rd_edge(edge_a, edge_b, degree_ab):  
        return math.sqrt(edge_a * edge_a + edge_b * edge_b - 2 * edge_a * edge_b * math.cos(FlushVolCalculator.to_radians(degree_ab)))  
    
    @staticmethod
    def DeltaHS_BBS(h1, s1, v1, h2, s2, v2):  
        h1_rad = FlushVolCalculator.to_radians(h1)  
        h2_rad = FlushVolCalculator.to_radians(h2)  
    
        dx = math.cos(h1_rad) * s1 * v1 - math.cos(h2_rad) * s2 * v2  
        dy = math.sin(h1_rad) * s1 * v1 - math.sin(h2_rad) * s2 * v2  
        dxy = math.sqrt(dx * dx + dy * dy)  
        return min(1.2, dxy)
    
    @staticmethod
    def hex_to_rgb(hex_color):
        # 
        hex_color = hex_color.lstrip('#')

        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])
        
        if len(hex_color) != 6:
            raise ValueError("Invalid hex color code, it should be 3 or 6 digits long")
        
        color_value = int(hex_color, 16)
        
        r = (color_value >> 16) & 0xFF
        g = (color_value >> 8) & 0xFF
        b = color_value & 0xFF
          
        return r, g, b


def generate_Flush_matrix(tool_colors):
    colors = tool_colors.split(',')

    result = []

    for from_color in colors:
        for to_color in colors:
            # You can just use the default values here. The flush parameters multiplier can be modified in the wash flush, such as 'blobifier'.
            flush_vol_calc1 = FlushVolCalculator(0,800,1.0)    
            volume = flush_vol_calc1.calc_flush_vol_by_hex(from_color, to_color)
            result.append(str(volume))
        
    return ",".join(result)

def main():
    flush_vol_calc = FlushVolCalculator(0,800,1.0)
    flush_vol = flush_vol_calc.calc_flush_vol_by_rgb(192, 192, 192, 247, 35, 35)
    print(f"The flush vol from RGB color 192, 192, 192 to 247, 35, 35 is: {flush_vol}")
    
    flush_vol = flush_vol_calc.calc_flush_vol_by_hex("#C0C0C0", "#F72323")
    print(f"The flush vol from hex color #C0C0C0 to #F72323 is: {flush_vol}")

    flush_vol = flush_vol_calc.calc_flush_vol_by_hex("C0C0C0", "F72323")
    print(f"The flush vol from hex color C0C0C0 to F72323 is:{flush_vol}")

    TOOL_COLORS="FFFF00,80FFFF,FFFFFF,FF8000"
    PURGE_VOLUMES = generate_Flush_matrix(TOOL_COLORS)
    print(f"\nDate: TOOL_COLORS={TOOL_COLORS} \nResult: PURGE_VOLUMES={PURGE_VOLUMES}")



if __name__ == "__main__":  
    main()  

