import math

def calculate_moment(span_m, load_knm):
    """Calculates design bending moment (Mu) with 1.5 safety factor."""
    factored_load = 1.5 * load_knm
    return (factored_load * (span_m**2)) / 8

def calculate_steel_area(moment_kNm, steel_grade_fy, effective_depth_mm, width_mm):
    """Calculates Ast based on LSM principles and IS 456 minimums."""
    moment_nmm = moment_kNm * 10**6
    # Required steel based on simplified lever arm (d - 0.42xu_max) would be more accurate, 
    # but this remains standard for preliminary chatbot estimation.
    required_ast = moment_nmm / (0.87 * steel_grade_fy * (effective_depth_mm * 0.9)) # Using approx lever arm 0.9d
    minimum_ast = (0.85 * width_mm * effective_depth_mm) / steel_grade_fy
    return round(max(required_ast, minimum_ast), 2)

def check_structural_limits(moment_kNm, concrete_grade_fck, steel_grade_fy, width_mm, effective_depth_mm, span_m):
    """Evaluates Mu_lim and Span-to-depth (serviceability)."""
    grade_factors = {250: 0.53, 415: 0.48, 500: 0.46}
    xu_max_factor = grade_factors.get(steel_grade_fy, 0.48)
    
    max_neutral_axis_depth = xu_max_factor * effective_depth_mm
    limiting_moment_kNm = (0.36 * concrete_grade_fck * width_mm * max_neutral_axis_depth * (effective_depth_mm - 0.42 * max_neutral_axis_depth)) / 10**6
    span_to_depth_ratio = (span_m * 1000) / effective_depth_mm
    
    return {
        "limiting_moment_kNm": round(limiting_moment_kNm, 2),
        "is_flexure_safe": moment_kNm <= limiting_moment_kNm,
        "is_deflection_safe": span_to_depth_ratio <= 20,
        "actual_span_to_depth_ratio": round(span_to_depth_ratio, 2)
    }

def select_reinforcement_bars(target_steel_area_mm2):
    """Optimizes bar selection to find the LEAST excess steel area."""
    available_diameters = [10, 12, 16, 20, 25] # Added 25mm for heavy loads
    best_config = None
    
    for diameter in available_diameters:
        area_of_single_bar = (math.pi / 4) * (diameter**2)
        number_of_bars = math.ceil(target_steel_area_mm2 / area_of_single_bar)
        total_area_provided = number_of_bars * area_of_single_bar
        excess = total_area_provided - target_steel_area_mm2
        
        # FIX: Changed > to < to find the most efficient bar count
        if best_config is None or excess < best_config["excess"]:
            best_config = {
                "bar_diameter_mm": diameter,
                "number_of_bars": number_of_bars,
                "steel_provided_mm2": round(total_area_provided, 2),
                "excess": round(excess, 2)
            }
    return best_config

def get_tau_c(fck, pt):
    """IS 456 Table 19 simplified lookup."""
    table = {
        20: [0.36, 0.48, 0.56, 0.62],
        25: [0.40, 0.52, 0.60, 0.67],
        30: [0.44, 0.56, 0.64, 0.72],
        35: [0.48, 0.60, 0.68, 0.76]
    }
    fck_key = min(table.keys(), key=lambda x: abs(x - fck))
    values = table[fck_key]

    if pt <= 0.25: return values[0]
    elif pt <= 0.50: return values[1]
    elif pt <= 0.75: return values[2]
    else: return values[3]

def perform_shear_check(span_m, load_knm, width_mm, effective_depth_mm, steel_provided_mm2, fck):
    """Full IS 456 compliant shear check logic."""
    factored_load = 1.5 * load_knm
    Vu = (factored_load * span_m / 2) * 1000 
    tau_v = Vu / (width_mm * effective_depth_mm)
    pt = (100 * steel_provided_mm2) / (width_mm * effective_depth_mm)
    
    tau_c = get_tau_c(fck, pt)
    tau_c_max = 0.62 * math.sqrt(fck)

    # FIX: Clarified that minimum stirrups are required even if tau_v < tau_c
    if tau_v <= tau_c:
        status = "MINIMUM SHEAR REINFORCEMENT REQUIRED"
    elif tau_v < tau_c_max:
        status = "DESIGN SHEAR REINFORCEMENT REQUIRED"
    else:
        status = "FAIL (Section inadequate for shear)"

    return {
        "tau_v": round(tau_v, 3),
        "tau_c": tau_c,
        "tau_c_max": round(tau_c_max, 3),
        "pt": round(pt, 3),
        "status": status
    }

def design_rc_beam_chatbot_entry(data):
    """Orchestration function with verified safety logic."""
    try:
        L, w, fck, fy, b, d = data['L'], data['w'], data['fck'], data['fy'], data['b'], data['d']
        
        if any(val <= 0 for val in [L, fck, fy, b, d]):
            return {"error": "Input values must be positive."}

        moment = calculate_moment(L, w)
        required_steel = calculate_steel_area(moment, fy, d, b)
        bars = select_reinforcement_bars(required_steel)
        limits = check_structural_limits(moment, fck, fy, b, d, L)
        shear = perform_shear_check(L, w, b, d, bars["steel_provided_mm2"], fck)
        
        max_allowed_steel = 0.04 * b * d
        is_flexure_safe = limits["is_flexure_safe"]
        is_deflection_safe = limits["is_deflection_safe"]
        is_steel_safe = bars["steel_provided_mm2"] <= max_allowed_steel
        
        design_status = "SAFE" if (is_flexure_safe and is_deflection_safe and is_steel_safe and "FAIL" not in shear["status"]) else "UNSAFE"
        
        suggestions = []
        if not is_flexure_safe:
            suggestions.append("Section is Over-Reinforced. Increase depth (d) or width (b).")
        if not is_deflection_safe:
            suggestions.append("Deflection failure. Increase depth (d).")
        if bars["number_of_bars"] > 6:
            suggestions.append(f"Congestion alert: {bars['number_of_bars']} bars is too many for {b}mm width. Use larger diameter bars.")
        if "REINFORCEMENT REQUIRED" in shear["status"]:
            suggestions.append("Provide stirrups as per IS 456 shear design tables.")
        elif "FAIL" in shear["status"]:
            suggestions.append("Shear stress exceeds maximum limit. Increase beam size.")

        return {
            "ultimate_moment_kNm": round(moment, 2),
            "limiting_moment_kNm": limits["limiting_moment_kNm"],
            "reinforcement": f"{bars['number_of_bars']}-{bars['bar_diameter_mm']}mm diameter bars",
            "shear_status": shear["status"],
            "design_status": design_status,
            "suggestions": suggestions,
            "explanation": {
                "flexure": "Under-reinforced" if is_flexure_safe else "Over-reinforced (Brittle)",
                "shear": f"tau_v({shear['tau_v']}) vs tau_c({shear['tau_c']})",
                "deflection": f"L/d actual: {limits['actual_span_to_depth_ratio']} (Limit: 20)"
            }
        }
    except Exception as e:
        return {"error": str(e)}