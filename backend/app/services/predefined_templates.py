from typing import Any, Dict, List
import uuid

def get_predefined_projects() -> List[Dict[str, Any]]:
    """
    Returns pre-configured simulation project structures for key target domains.
    Includes 8 domain models (Startup, Smart City, Agriculture, College, Retail, Hospital, Supply Chain, Disaster).
    """
    templates = []

    # 1. Startup Company Simulation Template
    startup_template = {
        "id": "template_startup",
        "name": "Startup Growth & Run Rate Simulator",
        "description": "Models user growth, cash burn rate, employee headcount, and runway under varying market conditions.",
        "domain": "startup",
        "layout": {
            "nodes": [
                {"id": "n1", "type": "stock", "position": {"x": 100, "y": 150}, "data": {"label": "Cash Reserves ($)"}},
                {"id": "n2", "type": "flow", "position": {"x": 300, "y": 150}, "data": {"label": "Monthly Revenue ($)"}},
                {"id": "n3", "type": "flow", "position": {"x": 100, "y": 300}, "data": {"label": "Cash Burn Rate ($)"}},
                {"id": "n4", "type": "agent", "position": {"x": 500, "y": 150}, "data": {"label": "Sales Reps"}},
                {"id": "n5", "type": "agent", "position": {"x": 500, "y": 300}, "data": {"label": "Software Engineers"}}
            ],
            "edges": [
                {"id": "e1", "source": "n4", "target": "n2", "label": "generates sales"},
                {"id": "e2", "source": "n5", "target": "n3", "label": "payroll cost"}
            ]
        },
        "global_variables": {
            "market_demand": 1.2,
            "interest_rate": 0.05,
            "competitor_strength": 0.8
        },
        "agents": [
            {
                "id": "sales_1",
                "name": "Mid-Market Sales Team",
                "role": "sales",
                "agent_type": "employee",
                "goals": ["maximize_deals"],
                "personality": {"risk_tolerance": 0.7, "extraversion": 0.9, "conscientiousness": 0.6, "agreeableness": 0.7, "neuroticism": 0.3},
                "resources": {"salary": 6000.0, "productivity": 80.0},
                "state": {"pipeline_deals": 5},
                "memory": [],
                "relationships": {},
                "is_active": True
            },
            {
                "id": "eng_1",
                "name": "Core Platform Engineering",
                "role": "engineering",
                "agent_type": "employee",
                "goals": ["improve_product_stability"],
                "personality": {"risk_tolerance": 0.3, "extraversion": 0.4, "conscientiousness": 0.9, "agreeableness": 0.6, "neuroticism": 0.5},
                "resources": {"salary": 8500.0, "stability": 95.0},
                "state": {"bugs_count": 12},
                "memory": [],
                "relationships": {},
                "is_active": True
            }
        ],
        "rules": [
            {
                "id": "r_startup_1",
                "name": "Revenue Generation",
                "description": "Calculate monthly revenue based on sales rep productivity and market demand.",
                "condition": "agent.role == 'sales' and global.market_demand > 0.5",
                "action": "global.monthly_revenue += (agent.resources['productivity'] * 150 * global.market_demand); agent.state['pipeline_deals'] += 1",
                "priority": 10,
                "probability": 1.0
            },
            {
                "id": "r_startup_2",
                "name": "Payroll Burn",
                "description": "Add salaries of active workforce to cash burn rate.",
                "condition": "agent.is_active == True",
                "action": "global.cash_burn_rate += agent.resources['salary']",
                "priority": 5,
                "probability": 1.0
            }
        ],
        "system_dynamics": {
            "stocks": {
                "cash": {
                    "id": "cash",
                    "name": "Cash Balance",
                    "initial_value": 500000.0,
                    "inflows": ["revenue"],
                    "outflows": ["burn"]
                }
            },
            "flows": {
                "revenue": {
                    "id": "revenue",
                    "name": "Inflow Revenue",
                    "expression": "variables.monthly_revenue"
                },
                "burn": {
                    "id": "burn",
                    "name": "Monthly Expenditures",
                    "expression": "variables.cash_burn_rate"
                }
            },
            "auxiliaries": {
                "monthly_revenue": {
                    "id": "monthly_revenue",
                    "name": "Base Monthly Revenue",
                    "expression": "5000.0 * constants.market_demand"
                },
                "cash_burn_rate": {
                    "id": "cash_burn_rate",
                    "name": "Workforce Operating Cost",
                    "expression": "15000.0 + 800.0"
                }
            },
            "constants": {
                "market_demand": 1.2
            }
        }
    }

    # 2. Smart City Infrastructure Simulator Template
    city_template = {
        "id": "template_smart_city",
        "name": "Smart City Grid & Transit System",
        "description": "Monitors commute times, power grids, vehicle counts, and residential densities.",
        "domain": "smart_city",
        "layout": {
            "nodes": [
                {"id": "c1", "type": "stock", "position": {"x": 100, "y": 100}, "data": {"label": "Grid Electricity (MWh)"}},
                {"id": "c2", "type": "flow", "position": {"x": 300, "y": 100}, "data": {"label": "Solar Power Input"}},
                {"id": "c3", "type": "agent", "position": {"x": 100, "y": 250}, "data": {"label": "Electric Vehicles"}},
                {"id": "c4", "type": "agent", "position": {"x": 350, "y": 250}, "data": {"label": "Smart Substations"}}
            ],
            "edges": []
        },
        "global_variables": {
            "solar_radiation": 8.0,
            "grid_demand": 2500.0,
            "traffic_density": 0.4
        },
        "agents": [
            {
                "id": "substation_1",
                "name": "Substation Alpha",
                "role": "grid_distribution",
                "agent_type": "infrastructure",
                "goals": ["balance_load"],
                "personality": {"risk_tolerance": 0.2, "extraversion": 0.5, "conscientiousness": 0.9, "agreeableness": 0.5, "neuroticism": 0.1},
                "resources": {"load_capacity": 5000.0, "current_load": 2200.0},
                "state": {"temperature_celsius": 42},
                "memory": [],
                "relationships": {},
                "is_active": True
            }
        ],
        "rules": [
            {
                "id": "r_city_1",
                "name": "Solar Grid Input",
                "description": "Increases grid capacity during high sunlight hours.",
                "condition": "global.solar_radiation > 5.0",
                "action": "global.grid_demand -= (global.solar_radiation * 120)",
                "priority": 10,
                "probability": 1.0
            }
        ],
        "system_dynamics": {
            "stocks": {
                "grid_reserves": {
                    "id": "grid_reserves",
                    "name": "Power Bank Status",
                    "initial_value": 100000.0,
                    "inflows": ["solar_in"],
                    "outflows": ["consumption"]
                }
            },
            "flows": {
                "solar_in": {
                    "id": "solar_in",
                    "name": "Solar Harvesting",
                    "expression": "1000.0 * constants.solar_radiation"
                },
                "consumption": {
                    "id": "consumption",
                    "name": "Household Demand",
                    "expression": "2500.0 + variables.traffic_factor"
                }
            },
            "auxiliaries": {
                "traffic_factor": {
                    "id": "traffic_factor",
                    "name": "Traffic Load Auxiliary",
                    "expression": "constants.traffic_density * 500"
                }
            },
            "constants": {
                "solar_radiation": 8.0,
                "traffic_density": 0.4
            }
        }
    }

    # 3. Crop Yield & Agro-Climate Template
    crop_template = {
        "id": "template_crop_yield",
        "name": "Crop Growth & Soil Degradation Simulator",
        "description": "Simulates soil moisture, rainfall effects, nitrogen updates, and harvest yields.",
        "domain": "agriculture",
        "layout": {
            "nodes": [
                {"id": "cr1", "type": "stock", "position": {"x": 100, "y": 100}, "data": {"label": "Soil Nitrogen (kg)"}},
                {"id": "cr2", "type": "stock", "position": {"x": 100, "y": 250}, "data": {"label": "Irrigation Water (m3)"}},
                {"id": "cr3", "type": "agent", "position": {"x": 350, "y": 180}, "data": {"label": "Wheat Crop Cell"}}
            ],
            "edges": []
        },
        "global_variables": {
            "rainfall_mm": 5.0,
            "soil_ph": 6.8,
            "ambient_temp": 24.5
        },
        "agents": [
            {
                "id": "crop_wheat_1",
                "name": "Wheat Field Sector A",
                "role": "crop",
                "agent_type": "biological",
                "goals": ["maximize_biomass"],
                "personality": {"risk_tolerance": 0.5, "extraversion": 0.5, "conscientiousness": 0.5, "agreeableness": 0.5, "neuroticism": 0.5},
                "resources": {"nitrogen_requirement": 10.0, "biomass": 1.0},
                "state": {"height_cm": 5, "days_to_maturity": 90},
                "memory": [],
                "relationships": {},
                "is_active": True
            }
        ],
        "rules": [
            {
                "id": "r_crop_1",
                "name": "Crop Photosynthesis",
                "description": "Increases biomass when water and sunlight are adequate.",
                "condition": "global.rainfall_mm > 1.0 and global.ambient_temp > 18.0",
                "action": "agent.resources['biomass'] += 0.4; agent.state['days_to_maturity'] -= 1",
                "priority": 10,
                "probability": 1.0
            }
        ],
        "system_dynamics": {
            "stocks": {
                "soil_moisture": {
                    "id": "soil_moisture",
                    "name": "Soil Volumetric Water Content",
                    "initial_value": 40.0,
                    "inflows": ["rain_in"],
                    "outflows": ["evaporation"]
                }
            },
            "flows": {
                "rain_in": {
                    "id": "rain_in",
                    "name": "Precipitation Inflow",
                    "expression": "constants.rainfall_mm * 1.5"
                },
                "evaporation": {
                    "id": "evaporation",
                    "name": "Water Loss",
                    "expression": "0.1 * constants.ambient_temp"
                }
            },
            "auxiliaries": {},
            "constants": {
                "rainfall_mm": 5.0,
                "ambient_temp": 24.5
            }
        }
    }

    # 4. College / University Policy Simulator Template
    college_template = {
        "id": "template_college",
        "name": "University Admissions & Funding Planner",
        "description": "Models student admissions, tuition earnings, course dropouts, and facilities endowment.",
        "domain": "university",
        "layout": {},
        "global_variables": {
            "tuition_fees": 12000.0,
            "acceptance_rate": 0.45,
            "reputation_index": 0.8
        },
        "agents": [
            {
                "id": "stud_1",
                "name": "Engineering Freshmen cohort",
                "role": "students",
                "agent_type": "academic",
                "goals": ["graduate"],
                "personality": {"risk_tolerance": 0.4, "extraversion": 0.7, "conscientiousness": 0.8, "agreeableness": 0.8, "neuroticism": 0.4},
                "resources": {"grades": 82.0, "morale": 90.0},
                "state": {"enrolled_count": 150},
                "memory": [],
                "relationships": {},
                "is_active": True
            }
        ],
        "rules": [
            {
                "id": "r_college_1",
                "name": "Tuition Adjustment Effects",
                "description": "High tuition fees lower student morale.",
                "condition": "global.tuition_fees > 15000",
                "action": "agent.resources['morale'] -= 5.0",
                "priority": 8,
                "probability": 1.0
            }
        ],
        "system_dynamics": {
            "stocks": {
                "endowment": {
                    "id": "endowment",
                    "name": "Endowment Fund",
                    "initial_value": 1500000.0,
                    "inflows": ["fees_in"],
                    "outflows": ["ops_out"]
                }
            },
            "flows": {
                "fees_in": {
                    "id": "fees_in",
                    "name": "Tuition Intake",
                    "expression": "constants.tuition_fees * 150"
                },
                "ops_out": {
                    "id": "ops_out",
                    "name": "Operational Overhead",
                    "expression": "500000.0"
                }
            },
            "auxiliaries": {},
            "constants": {
                "tuition_fees": 12000.0
            }
        }
    }

    # 5. Retail Store Inventory Simulator Template
    retail_template = {
        "id": "template_retail",
        "name": "Retail Store Supply Chain & Demand Simulator",
        "description": "Models consumer purchase patterns, stock replenishments, and back-orders.",
        "domain": "retail",
        "layout": {},
        "global_variables": {
            "marketing_spend": 2000.0,
            "competitor_price": 45.0,
            "unit_price": 49.99
        },
        "agents": [
            {
                "id": "buyer_1",
                "name": "Standard Customer Base",
                "role": "consumer",
                "agent_type": "buyer",
                "goals": ["buy_deals"],
                "personality": {"risk_tolerance": 0.6, "extraversion": 0.5, "conscientiousness": 0.5, "agreeableness": 0.7, "neuroticism": 0.3},
                "resources": {"demand_rate": 15.0},
                "state": {"items_purchased": 0},
                "memory": [],
                "relationships": {},
                "is_active": True
            }
        ],
        "rules": [
            {
                "id": "r_retail_1",
                "name": "Buyer Decision",
                "description": "Customers buy more if price is competitive.",
                "condition": "global.unit_price < global.competitor_price",
                "action": "agent.resources['demand_rate'] += 5.0; global.marketing_spend -= 100.0",
                "priority": 10,
                "probability": 1.0
            }
        ],
        "system_dynamics": {
            "stocks": {
                "inventory": {
                    "id": "inventory",
                    "name": "Store Inventory Level",
                    "initial_value": 500.0,
                    "inflows": ["replenish"],
                    "outflows": ["sales_out"]
                }
            },
            "flows": {
                "replenish": {
                    "id": "replenish",
                    "name": "Supplier Stocking",
                    "expression": "variables.reorder_rate"
                },
                "sales_out": {
                    "id": "sales_out",
                    "name": "Customer Purchases",
                    "expression": "100.0"
                }
            },
            "auxiliaries": {
                "reorder_rate": {
                    "id": "reorder_rate",
                    "name": "Reorder Quantity",
                    "expression": "200.0 if stocks.inventory < 200.0 else 0.0"
                }
            },
            "constants": {}
        }
    }

    # 6. Healthcare / Hospital Capacity Simulator
    hospital_template = {
        "id": "template_hospital",
        "name": "Healthcare & ICU Patient Allocation Simulator",
        "description": "Models ICU admission queues, patient recovery durations, doctor availability, and treatment safety factors.",
        "domain": "hospital",
        "layout": {
            "nodes": [
                {"id": "h1", "type": "stock", "position": {"x": 100, "y": 100}, "data": {"label": "Occupied Beds"}},
                {"id": "h2", "type": "flow", "position": {"x": 280, "y": 100}, "data": {"label": "Admissions Rate"}},
                {"id": "h3", "type": "agent", "position": {"x": 100, "y": 250}, "data": {"label": "Emergency Doctors"}}
            ],
            "edges": []
        },
        "global_variables": {
            "daily_arrivals": 25.0,
            "avg_stay_days": 6.0,
            "icu_limit": 50.0
        },
        "agents": [
            {
                "id": "doc_team_1",
                "name": "Emergency Shift Alpha",
                "role": "doctor",
                "agent_type": "clinical",
                "goals": ["reduce_wait_time", "minimize_mortality"],
                "personality": {"risk_tolerance": 0.4, "extraversion": 0.6, "conscientiousness": 0.95, "agreeableness": 0.8, "neuroticism": 0.2},
                "resources": {"stamina": 100.0, "treatment_speed": 12.0},
                "state": {"patients_discharged": 0},
                "memory": [],
                "relationships": {},
                "is_active": True
            }
        ],
        "rules": [
            {
                "id": "r_hosp_1",
                "name": "Doctor Exhaustion Rule",
                "description": "Stamina depletes if daily admissions exceed treatment capacity.",
                "condition": "global.daily_arrivals > (agent.resources['treatment_speed'] * 1.5)",
                "action": "agent.resources['stamina'] -= 8.0; agent.resources['treatment_speed'] *= 0.9",
                "priority": 10,
                "probability": 1.0
            }
        ],
        "system_dynamics": {
            "stocks": {
                "occupied_beds": {
                    "id": "occupied_beds",
                    "name": "Active Occupied Ward Beds",
                    "initial_value": 30.0,
                    "inflows": ["admission_flow"],
                    "outflows": ["discharge_flow"]
                }
            },
            "flows": {
                "admission_flow": {
                    "id": "admission_flow",
                    "name": "Inflow Intake",
                    "expression": "constants.daily_arrivals"
                },
                "discharge_flow": {
                    "id": "discharge_flow",
                    "name": "Discharge Recovery Rate",
                    "expression": "stocks.occupied_beds / constants.avg_stay_days"
                }
            },
            "auxiliaries": {},
            "constants": {
                "daily_arrivals": 25.0,
                "avg_stay_days": 6.0
            }
        }
    }

    # 7. Supply Chain & Freight Logistics Simulator
    supply_chain_template = {
        "id": "template_supply_chain",
        "name": "Global Multi-Tier Logistics & Order Fulfillment Simulator",
        "description": "Models factory manufacturing outputs, container freight delays, customer demand fluctuations, and backorders.",
        "domain": "logistics",
        "layout": {},
        "global_variables": {
            "order_rate": 120.0,
            "transit_days": 4.0,
            "production_rate": 150.0
        },
        "agents": [
            {
                "id": "carrier_1",
                "name": "Ocean Freight Logistics Group",
                "role": "shipping",
                "agent_type": "carrier",
                "goals": ["minimize_transit_delays"],
                "personality": {"risk_tolerance": 0.5, "extraversion": 0.5, "conscientiousness": 0.85, "agreeableness": 0.6, "neuroticism": 0.4},
                "resources": {"fuel": 1000.0, "efficiency": 92.0},
                "state": {"shipments_in_transit": 3},
                "memory": [],
                "relationships": {},
                "is_active": True
            }
        ],
        "rules": [
            {
                "id": "r_sc_1",
                "name": "Freight Surcharges & Delays",
                "description": "Low container fuel efficiency delays delivery times.",
                "condition": "agent.resources['efficiency'] < 90.0",
                "action": "global.transit_days += 1.5; agent.resources['fuel'] -= 20.0",
                "priority": 10,
                "probability": 1.0
            }
        ],
        "system_dynamics": {
            "stocks": {
                "warehouse_stock": {
                    "id": "warehouse_stock",
                    "name": "Warehouse Finished Goods",
                    "initial_value": 1500.0,
                    "inflows": ["production_inflow"],
                    "outflows": ["shipment_outflow"]
                }
            },
            "flows": {
                "production_inflow": {
                    "id": "production_inflow",
                    "name": "Manufacturing Output",
                    "expression": "constants.production_rate"
                },
                "shipment_outflow": {
                    "id": "shipment_outflow",
                    "name": "Outflow Delivery",
                    "expression": "min(stocks.warehouse_stock, constants.order_rate)"
                }
            },
            "auxiliaries": {},
            "constants": {
                "order_rate": 120.0,
                "production_rate": 150.0
            }
        }
    }

    # 8. Disaster Response & Crisis Evacuation Simulator
    disaster_template = {
        "id": "template_disaster",
        "name": "Disaster Management & Flood Evacuation Simulator",
        "description": "Models rising flood levels, shelter capacities, dispatch safety routes, and emergency response teams.",
        "domain": "disaster_management",
        "layout": {},
        "global_variables": {
            "precipitation_rate": 45.0,
            "evacuation_speed": 150.0,
            "shelter_limit": 1000.0
        },
        "agents": [
            {
                "id": "rescue_1",
                "name": "First Responder Team Alpha",
                "role": "rescue",
                "agent_type": "emergency",
                "goals": ["maximize_lives_saved"],
                "personality": {"risk_tolerance": 0.8, "extraversion": 0.8, "conscientiousness": 0.9, "agreeableness": 0.8, "neuroticism": 0.1},
                "resources": {"stamina": 100.0, "rescue_capacity": 50.0},
                "state": {"rescued_count": 0},
                "memory": [],
                "relationships": {},
                "is_active": True
            }
        ],
        "rules": [
            {
                "id": "r_disaster_1",
                "name": "High Precipitation Block",
                "description": "Increases danger level and slows down rescue team evacuation speed.",
                "condition": "global.precipitation_rate > 35.0",
                "action": "global.evacuation_speed *= 0.8; agent.resources['stamina'] -= 5.0",
                "priority": 10,
                "probability": 1.0
            }
        ],
        "system_dynamics": {
            "stocks": {
                "flooded_zones": {
                    "id": "flooded_zones",
                    "name": "Submerged Land Areas (acres)",
                    "initial_value": 10.0,
                    "inflows": ["water_rise"],
                    "outflows": ["drainage"]
                }
            },
            "flows": {
                "water_rise": {
                    "id": "water_rise",
                    "name": "Flooding Rate",
                    "expression": "constants.precipitation_rate * 0.4"
                },
                "drainage": {
                    "id": "drainage",
                    "name": "Pumping Outflow",
                    "expression": "5.0"
                }
            },
            "auxiliaries": {},
            "constants": {
                "precipitation_rate": 45.0
            }
        }
    }

    # 9. Climate Resilience & Agri-Tech Kit
    climate_agri_template = {
        "id": "template_climate_agri",
        "name": "Climate Resilience & Food Security Simulator",
        "description": "Models heatwaves, groundwater depletion, carbon offsets, and crop yield under extreme weather shocks.",
        "domain": "agriculture",
        "layout": {
            "nodes": [
                {"id": "n1", "type": "stock", "position": {"x": 100, "y": 150}, "data": {"label": "Groundwater Table (m)"}},
                {"id": "n2", "type": "flow", "position": {"x": 300, "y": 150}, "data": {"label": "Aquifer Recharge"}},
                {"id": "n3", "type": "stock", "position": {"x": 500, "y": 150}, "data": {"label": "Crop Yield Index"}}
            ],
            "edges": [{"id": "e1", "source": "n1", "target": "n3", "label": "irrigation supply"}]
        },
        "global_variables": {"ambient_temp": 32.0, "co2_ppm": 420.0, "rainfall_mm": 12.0},
        "agents": [],
        "rules": [],
        "system_dynamics": {
            "stocks": {
                "groundwater": {"id": "groundwater", "name": "Aquifer Level", "initial_value": 85.0, "inflows": ["recharge"], "outflows": ["irrigation_pumping"]}
            },
            "flows": {
                "recharge": {"id": "recharge", "name": "Rainfall Infiltration", "expression": "constants.rainfall_mm * 0.8"},
                "irrigation_pumping": {"id": "irrigation_pumping", "name": "Agricultural Pumping", "expression": "15.0"}
            },
            "auxiliaries": {},
            "constants": {"rainfall_mm": 12.0}
        }
    }

    # 10. Smart Grid & EV Infrastructure Kit
    smart_grid_template = {
        "id": "template_smart_grid",
        "name": "Smart Power Grid & EV Charger Load Simulator",
        "description": "Simulates transformer load, renewable energy generation spikes, EV fast-charging demand, and blackout risks.",
        "domain": "smart_city",
        "layout": {
            "nodes": [
                {"id": "n1", "type": "stock", "position": {"x": 150, "y": 150}, "data": {"label": "Grid Battery Reserve (MWh)"}},
                {"id": "n2", "type": "flow", "position": {"x": 350, "y": 150}, "data": {"label": "EV Charging Draw (MW)"}}
            ],
            "edges": []
        },
        "global_variables": {"ev_fleet_size": 4500, "solar_capacity_mw": 120.0, "grid_frequency": 50.0},
        "agents": [],
        "rules": [],
        "system_dynamics": {
            "stocks": {
                "battery_reserve": {"id": "battery_reserve", "name": "Substation Storage", "initial_value": 450.0, "inflows": ["solar_inflow"], "outflows": ["ev_draw"]}
            },
            "flows": {
                "solar_inflow": {"id": "solar_inflow", "name": "Solar Power Input", "expression": "75.0"},
                "ev_draw": {"id": "ev_draw", "name": "EV Fleet Power Demand", "expression": "60.0"}
            },
            "auxiliaries": {},
            "constants": {}
        }
    }

    # 11. Global Supply Chain Fragility Kit
    supply_chain_fragility_template = {
        "id": "template_supply_chain_fragility",
        "name": "Global Maritime Supply Chain Bottleneck Simulator",
        "description": "Simulates port congestion, container shortages, canal blockages, and retail inventory bullwhip effects.",
        "domain": "supply_chain",
        "layout": {},
        "global_variables": {"port_congestion_index": 7.8, "freight_rate_usd": 4200.0, "lead_time_days": 18.0},
        "agents": [],
        "rules": [],
        "system_dynamics": {
            "stocks": {
                "port_backlog": {"id": "port_backlog", "name": "Containers Waiting at Port", "initial_value": 8500.0, "inflows": ["ship_arrivals"], "outflows": ["customs_cleared"]}
            },
            "flows": {
                "ship_arrivals": {"id": "ship_arrivals", "name": "Inbound Cargo Vessels", "expression": "1200.0"},
                "customs_cleared": {"id": "customs_cleared", "name": "Unloaded & Processed", "expression": "950.0"}
            },
            "auxiliaries": {},
            "constants": {}
        }
    }

    # 12. Hospital Emergency Response Kit
    hospital_response_template = {
        "id": "template_hospital_response",
        "name": "Hospital Emergency Triage & Pandemic Bed Simulator",
        "description": "Models ICU admission rates, nurse-to-patient ratios, ventilator reserves, and emergency room queue dynamics.",
        "domain": "hospital",
        "layout": {},
        "global_variables": {"icu_beds_total": 120, "nurse_staff_on_shift": 45, "infection_r0": 2.4},
        "agents": [],
        "rules": [],
        "system_dynamics": {
            "stocks": {
                "icu_occupancy": {"id": "icu_occupancy", "name": "Occupied ICU Beds", "initial_value": 82.0, "inflows": ["admissions"], "outflows": ["discharges"]}
            },
            "flows": {
                "admissions": {"id": "admissions", "name": "ER Admissions", "expression": "14.0"},
                "discharges": {"id": "discharges", "name": "Recovered Discharges", "expression": "11.0"}
            },
            "auxiliaries": {},
            "constants": {}
        }
    }

    templates.extend([
        startup_template,
        city_template,
        crop_template,
        college_template,
        retail_template,
        hospital_template,
        supply_chain_template,
        disaster_template,
        climate_agri_template,
        smart_grid_template,
        supply_chain_fragility_template,
        hospital_response_template
    ])
    
    return templates
