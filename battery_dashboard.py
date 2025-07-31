import streamlit as st
import random
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Battery Cell Monitoring Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .charging-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin: 0.5rem 0;
    }
    .discharging-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin: 0.5rem 0;
    }
    .idle-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin: 0.5rem 0;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .charging-badge {
        background-color: #28a745;
        color: white;
    }
    .discharging-badge {
        background-color: #dc3545;
        color: white;
    }
    .idle-badge {
        background-color: #17a2b8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'cells_data' not in st.session_state:
        st.session_state.cells_data = {}
    if 'cell_types' not in st.session_state:
        st.session_state.cell_types = []
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False

def get_cell_specs(cell_type):
    """Get cell specifications based on type"""
    if cell_type.lower() == "lfp":
        return {
            "nominal_voltage": 3.2,
            "min_voltage": 2.8,
            "max_voltage": 3.6,
            "nominal_capacity": 100  # Ah
        }
    elif cell_type.lower() == "nmc":
        return {
            "nominal_voltage": 3.6,
            "min_voltage": 3.2,
            "max_voltage": 4.0,
            "nominal_capacity": 120  # Ah
        }
    else:
        return {
            "nominal_voltage": 3.7,
            "min_voltage": 3.0,
            "max_voltage": 4.2,
            "nominal_capacity": 110  # Ah
        }

def calculate_soc_percentage(voltage, min_voltage, max_voltage):
    """Calculate State of Charge percentage based on voltage"""
    return max(0, min(100, ((voltage - min_voltage) / (max_voltage - min_voltage)) * 100))

def get_cell_status(current):
    """Determine cell status based on current"""
    if current > 0.1:
        return "Charging", "charging"
    elif current < -0.1:
        return "Discharging", "discharging"
    else:
        return "Idle", "idle"

def setup_cells():
    """Setup cells configuration"""
    st.header("🔋 Battery Cell Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Bench Information")
        bench_name = st.text_input("Bench Name", value="Test Bench 1")
        group_num = st.number_input("Group Number", min_value=1, max_value=10, value=1)
    
    with col2:
        st.subheader("Cell Configuration")
        num_cells = st.number_input("Number of Cells", min_value=1, max_value=16, value=8)
    
    st.subheader("Cell Types")
    cell_types = []
    
    cols = st.columns(4)
    for i in range(num_cells):
        with cols[i % 4]:
            cell_type = st.selectbox(
                f"Cell {i+1} Type",
                options=["LFP", "NMC", "LTO"],
                key=f"cell_type_{i}"
            )
            cell_types.append(cell_type)
    
    if st.button("Initialize Cells", type="primary"):
        cells_data = {}
        
        for idx, cell_type in enumerate(cell_types, start=1):
            cell_key = f"cell_{idx}_{cell_type.lower()}"
            specs = get_cell_specs(cell_type)
            
            # Initialize with random values
            voltage = round(random.uniform(specs["min_voltage"], specs["max_voltage"]), 2)
            current = 0.0
            temp = round(random.uniform(25, 40), 1)
            capacity = round(voltage * abs(current), 2)
            soc = calculate_soc_percentage(voltage, specs["min_voltage"], specs["max_voltage"])
            
            cells_data[cell_key] = {
                "voltage": voltage,
                "current": current,
                "temp": temp,
                "capacity": capacity,
                "min_voltage": specs["min_voltage"],
                "max_voltage": specs["max_voltage"],
                "nominal_voltage": specs["nominal_voltage"],
                "nominal_capacity": specs["nominal_capacity"],
                "soc": soc,
                "cell_type": cell_type.upper()
            }
        
        st.session_state.cells_data = cells_data
        st.session_state.cell_types = cell_types
        st.session_state.setup_complete = True
        st.success(f"Successfully initialized {num_cells} cells!")
        st.rerun()

def display_cell_cards():
    """Display cell information in card format"""
    st.header("📊 Cell Status Dashboard")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_cells = len(st.session_state.cells_data)
    charging_cells = sum(1 for cell in st.session_state.cells_data.values() if cell['current'] > 0.1)
    discharging_cells = sum(1 for cell in st.session_state.cells_data.values() if cell['current'] < -0.1)
    avg_temp = sum(cell['temp'] for cell in st.session_state.cells_data.values()) / total_cells if total_cells > 0 else 0
    
    with col1:
        st.metric("Total Cells", total_cells)
    with col2:
        st.metric("Charging", charging_cells, delta=f"{charging_cells}")
    with col3:
        st.metric("Discharging", discharging_cells, delta=f"{discharging_cells}")
    with col4:
        st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
    
    # Cell cards
    st.subheader("Individual Cell Status")
    
    # Create columns for cards (4 cards per row)
    cells_list = list(st.session_state.cells_data.items())
    rows = [cells_list[i:i+4] for i in range(0, len(cells_list), 4)]
    
    for row in rows:
        cols = st.columns(len(row))
        
        for idx, (cell_key, cell_data) in enumerate(row):
            with cols[idx]:
                status, status_class = get_cell_status(cell_data['current'])
                
                # Determine card style based on status
                if status_class == "charging":
                    card_class = "charging-card"
                    badge_class = "charging-badge"
                elif status_class == "discharging":
                    card_class = "discharging-card"
                    badge_class = "discharging-badge"
                else:
                    card_class = "idle-card"
                    badge_class = "idle-badge"
                
                # Create card content
                st.markdown(f"""
                <div class="{card_class}">
                    <h4 style="margin-top: 0;">{cell_key.replace('_', ' ').title()}</h4>
                    <span class="status-badge {badge_class}">{status}</span>
                    <hr style="border-color: rgba(255,255,255,0.3);">
                    <p><strong>Voltage:</strong> {cell_data['voltage']:.2f}V</p>
                    <p><strong>Current:</strong> {cell_data['current']:.2f}A</p>
                    <p><strong>Temperature:</strong> {cell_data['temp']:.1f}°C</p>
                    <p><strong>SOC:</strong> {cell_data['soc']:.1f}%</p>
                    <p><strong>Capacity:</strong> {cell_data['capacity']:.2f}Wh</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Progress bar for SOC
                st.progress(cell_data['soc'] / 100)

def control_panel():
    """Control panel for updating cell values"""
    st.header("🎛️ Control Panel")
    
    with st.expander("Manual Current Control", expanded=True):
        st.subheader("Set Current Values")
        
        # Quick preset buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🔋 Start Charging (+2A)"):
                for cell_key in st.session_state.cells_data:
                    st.session_state.cells_data[cell_key]['current'] = 2.0
                    update_cell_calculations(cell_key)
                st.rerun()
        
        with col2:
            if st.button("⚡ Fast Charge (+5A)"):
                for cell_key in st.session_state.cells_data:
                    st.session_state.cells_data[cell_key]['current'] = 5.0
                    update_cell_calculations(cell_key)
                st.rerun()
        
        with col3:
            if st.button("🔻 Discharge (-2A)"):
                for cell_key in st.session_state.cells_data:
                    st.session_state.cells_data[cell_key]['current'] = -2.0
                    update_cell_calculations(cell_key)
                st.rerun()
        
        with col4:
            if st.button("⏸️ Stop All (0A)"):
                for cell_key in st.session_state.cells_data:
                    st.session_state.cells_data[cell_key]['current'] = 0.0
                    update_cell_calculations(cell_key)
                st.rerun()
        
        st.divider()
        
        # Individual cell controls
        st.subheader("Individual Cell Controls")
        cells_per_row = 4
        cell_keys = list(st.session_state.cells_data.keys())
        
        for i in range(0, len(cell_keys), cells_per_row):
            cols = st.columns(cells_per_row)
            row_cells = cell_keys[i:i+cells_per_row]
            
            for idx, cell_key in enumerate(row_cells):
                with cols[idx]:
                    current_val = st.number_input(
                        f"{cell_key.replace('_', ' ').title()}",
                        min_value=-10.0,
                        max_value=10.0,
                        value=st.session_state.cells_data[cell_key]['current'],
                        step=0.1,
                        key=f"current_{cell_key}",
                        help="Positive = Charging, Negative = Discharging"
                    )
                    
                    if current_val != st.session_state.cells_data[cell_key]['current']:
                        st.session_state.cells_data[cell_key]['current'] = current_val
                        update_cell_calculations(cell_key)

def update_cell_calculations(cell_key):
    """Update cell calculations based on current"""
    cell_data = st.session_state.cells_data[cell_key]
    
    # Update capacity (simplified calculation)
    cell_data['capacity'] = round(cell_data['voltage'] * abs(cell_data['current']), 2)
    
    # Simulate voltage change based on current (simplified model)
    if cell_data['current'] > 0:  # Charging
        voltage_change = min(0.1, cell_data['current'] * 0.02)
        cell_data['voltage'] = min(cell_data['max_voltage'], 
                                 cell_data['voltage'] + voltage_change)
    elif cell_data['current'] < 0:  # Discharging
        voltage_change = min(0.1, abs(cell_data['current']) * 0.02)
        cell_data['voltage'] = max(cell_data['min_voltage'], 
                                 cell_data['voltage'] - voltage_change)
    
    # Update SOC
    cell_data['soc'] = calculate_soc_percentage(
        cell_data['voltage'], 
        cell_data['min_voltage'], 
        cell_data['max_voltage']
    )
    
    # Simulate temperature change
    if abs(cell_data['current']) > 1:
        temp_change = random.uniform(-1, 2)
        cell_data['temp'] = max(20, min(60, cell_data['temp'] + temp_change))

def analytics_dashboard():
    """Analytics and visualization dashboard"""
    st.header("📈 Analytics Dashboard")
    
    if not st.session_state.cells_data:
        st.warning("No cell data available. Please initialize cells first.")
        return
    
    # Create DataFrame for easier plotting
    df_data = []
    for cell_key, cell_data in st.session_state.cells_data.items():
        df_data.append({
            'Cell': cell_key.replace('_', ' ').title(),
            'Voltage': cell_data['voltage'],
            'Current': cell_data['current'],
            'Temperature': cell_data['temp'],
            'SOC': cell_data['soc'],
            'Capacity': cell_data['capacity'],
            'Type': cell_data['cell_type']
        })
    
    df = pd.DataFrame(df_data)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Voltage comparison
        fig_voltage = px.bar(df, x='Cell', y='Voltage', color='Type',
                           title='Cell Voltages', height=400)
        fig_voltage.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_voltage, use_container_width=True)
        
        # Current comparison
        fig_current = px.bar(df, x='Cell', y='Current', color='Type',
                           title='Cell Currents (A)', height=400)
        fig_current.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_current, use_container_width=True)
    
    with col2:
        # SOC comparison
        fig_soc = px.bar(df, x='Cell', y='SOC', color='Type',
                        title='State of Charge (%)', height=400)
        fig_soc.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_soc, use_container_width=True)
        
        # Temperature comparison
        fig_temp = px.bar(df, x='Cell', y='Temperature', color='Type',
                         title='Cell Temperatures (°C)', height=400)
        fig_temp.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Summary table
    st.subheader("📋 Detailed Data Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Sidebar
    st.sidebar.title("🔋 Battery Monitor")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Navigation",
        ["Setup", "Dashboard", "Control Panel", "Analytics"]
    )
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto Refresh (5s)", value=False)
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Reset button
    if st.sidebar.button("🔄 Reset All Data", type="secondary"):
        st.session_state.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Status:** " + ("✅ Ready" if st.session_state.setup_complete else "⚠️ Setup Required"))
    
    # Main content
    if page == "Setup" or not st.session_state.setup_complete:
        setup_cells()
    elif page == "Dashboard":
        if st.session_state.setup_complete:
            display_cell_cards()
        else:
            st.warning("Please complete setup first.")
    elif page == "Control Panel":
        if st.session_state.setup_complete:
            control_panel()
        else:
            st.warning("Please complete setup first.")
    elif page == "Analytics":
        if st.session_state.setup_complete:
            analytics_dashboard()
        else:
            st.warning("Please complete setup first.")

if __name__ == "__main__":
    main()
