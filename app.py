import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from simulation_engine import CleanEnergyStartup, TechType, FundingType

# Page configuration
st.set_page_config(
    page_title="CleanStart: Clean Energy Startup Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_game():
    """Initialize or reset the game"""
    if 'game_initialized' not in st.session_state:
        st.session_state.game_initialized = False
    if 'company' not in st.session_state:
        st.session_state.company = None
    if 'tech_selected' not in st.session_state:
        st.session_state.tech_selected = None


def create_financial_chart(history):
    """Create comprehensive financial performance chart"""
    if not history:
        return None
    
    df = pd.DataFrame([
        {
            'Quarter': m.quarter,
            'Cash': m.cash / 1_000_000,
            'Revenue': m.revenue / 1_000_000,
            'Net Income': m.net_income / 1_000_000,
        }
        for m in history
    ])
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Cash Position', 'Revenue & Profit', 'Market Share', 'Technology Level'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Cash
    fig.add_trace(
        go.Scatter(x=df['Quarter'], y=df['Cash'], name='Cash ($M)', 
                  line=dict(color='#1f77b4', width=3)),
        row=1, col=1
    )
    
    # Revenue and Net Income
    fig.add_trace(
        go.Bar(x=df['Quarter'], y=df['Revenue'], name='Revenue ($M)', 
               marker_color='#2ca02c'),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=df['Quarter'], y=df['Net Income'], name='Net Income ($M)', 
               marker_color='#ff7f0e'),
        row=1, col=2
    )
    
    # Market Share
    market_share_data = [m.market_share * 100 for m in history]
    fig.add_trace(
        go.Scatter(x=df['Quarter'], y=market_share_data, name='Market Share (%)', 
                  line=dict(color='#d62728', width=3), fill='tozeroy'),
        row=2, col=1
    )
    
    # Technology Level
    tech_data = [m.tech_level for m in history]
    fig.add_trace(
        go.Scatter(x=df['Quarter'], y=tech_data, name='Tech Level', 
                  line=dict(color='#9467bd', width=3)),
        row=2, col=2
    )
    
    fig.update_xaxes(title_text="Quarter", row=1, col=1)
    fig.update_xaxes(title_text="Quarter", row=1, col=2)
    fig.update_xaxes(title_text="Quarter", row=2, col=1)
    fig.update_xaxes(title_text="Quarter", row=2, col=2)
    
    fig.update_yaxes(title_text="Cash ($M)", row=1, col=1)
    fig.update_yaxes(title_text="Amount ($M)", row=1, col=2)
    fig.update_yaxes(title_text="Share (%)", row=2, col=1)
    fig.update_yaxes(title_text="Level", row=2, col=2)
    
    fig.update_layout(height=700, showlegend=True, title_text="Company Performance Dashboard")
    
    return fig


def create_competitor_chart(competitors):
    """Create competitor comparison chart"""
    active_competitors = [c for c in competitors if c.is_active]
    
    if not active_competitors:
        return None
    
    df = pd.DataFrame([
        {
            'Company': c.name,
            'Tech Level': c.tech_level,
            'Market Share': c.market_share * 100,
            'Price': c.price
        }
        for c in active_competitors
    ])
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Technology Level', 'Market Share'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    fig.add_trace(
        go.Bar(x=df['Company'], y=df['Tech Level'], name='Tech Level',
               marker_color='#17becf'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=df['Company'], y=df['Market Share'], name='Market Share (%)',
               marker_color='#bcbd22'),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False, title_text="Competitor Landscape")
    fig.update_yaxes(title_text="Tech Level", row=1, col=1)
    fig.update_yaxes(title_text="Share (%)", row=1, col=2)
    
    return fig


def render_game_start():
    """Render the game start screen"""
    st.markdown('<div class="main-header">⚡ CleanStart Simulator</div>', unsafe_allow_html=True)
    st.markdown("### Clean Energy Startup Simulation")
    st.markdown("Welcome to CleanStart! You are the CEO of a promising clean energy startup. "
                "Your mission: survive 12 quarters, achieve profitability, and maximize your company's valuation.")
    
    st.markdown("---")
    st.subheader("Choose Your Technology")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔋 Advanced Battery Storage")
        st.write("High unit cost, medium market size, strong R&D leverage")
        if st.button("Select Battery Technology", use_container_width=True):
            st.session_state.tech_selected = TechType.BATTERY
            
        st.markdown("#### 🌞 Next-Gen Solar Panels")
        st.write("Lower unit cost, large market size, high price competition")
        if st.button("Select Solar Technology", use_container_width=True):
            st.session_state.tech_selected = TechType.SOLAR
    
    with col2:
        st.markdown("#### 💧 Green Hydrogen Production")
        st.write("Highest unit cost, smaller market, excellent R&D potential")
        if st.button("Select Hydrogen Technology", use_container_width=True):
            st.session_state.tech_selected = TechType.HYDROGEN
            
        st.markdown("#### 🌍 Carbon Capture Technology")
        st.write("High unit cost, growing market, moderate R&D leverage")
        if st.button("Select Carbon Capture", use_container_width=True):
            st.session_state.tech_selected = TechType.CARBON_CAPTURE
    
    if st.session_state.tech_selected:
        st.success(f"✅ Selected: {st.session_state.tech_selected.value}")
        if st.button("🚀 Start Simulation", type="primary", use_container_width=True):
            st.session_state.company = CleanEnergyStartup(st.session_state.tech_selected)
            st.session_state.game_initialized = True
            st.rerun()


def render_game_over():
    """Render game over screen"""
    company = st.session_state.company
    state = company.get_current_state()
    
    st.markdown('<div class="main-header">🏁 Game Over</div>', unsafe_allow_html=True)
    
    if "Bankruptcy" in state['game_over_reason']:
        st.error(f"### {state['game_over_reason']}")
        st.markdown("Your company ran out of cash and was forced to shut down.")
    else:
        st.success(f"### {state['game_over_reason']}")
        st.markdown("Congratulations on completing 12 quarters!")
    
    st.markdown("---")
    
    # Final metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Final Valuation", f"${state['metrics'].valuation:,.0f}")
    with col2:
        st.metric("Total Revenue", f"${state['metrics'].revenue * state['metrics'].quarter:,.0f}")
    with col3:
        st.metric("Market Share", f"{state['metrics'].market_share * 100:.1f}%")
    with col4:
        st.metric("Tech Level", f"{state['metrics'].tech_level:.2f}")
    
    # Performance score
    score = (state['metrics'].valuation / 1_000_000 + 
             state['metrics'].market_share * 1000 + 
             state['metrics'].tech_level * 100)
    
    st.markdown("---")
    st.subheader(f"Final Score: {score:.0f} points")
    
    if score > 500:
        st.success("🌟 Outstanding Performance! You've built a industry-leading company.")
    elif score > 300:
        st.info("💼 Good Performance! Your company is on solid footing.")
    else:
        st.warning("📊 Room for Improvement. Consider different strategies next time.")
    
    # Show charts
    if state['history']:
        st.plotly_chart(create_financial_chart(state['history']), use_container_width=True)
    
    st.markdown("---")
    if st.button("🔄 Play Again", type="primary", use_container_width=True):
        st.session_state.game_initialized = False
        st.session_state.company = None
        st.session_state.tech_selected = None
        st.rerun()


def render_main_game():
    """Render the main game interface"""
    company = st.session_state.company
    state = company.get_current_state()
    
    # Header
    st.markdown(f'<div class="main-header">⚡ CleanStart - {state["tech_type"].value}</div>', 
                unsafe_allow_html=True)
    
    # Top metrics bar
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Quarter", f"{state['metrics'].quarter}/12")
    with col2:
        cash_color = "normal" if state['metrics'].cash >= 0 else "inverse"
        st.metric("💰 Cash", f"${state['metrics'].cash/1_000_000:.2f}M", 
                 delta_color=cash_color)
    with col3:
        st.metric("📈 Revenue", f"${state['metrics'].revenue/1_000:,.0f}K")
    with col4:
        profit_delta = "normal" if state['metrics'].net_income >= 0 else "inverse"
        st.metric("💵 Net Income", f"${state['metrics'].net_income/1_000:,.0f}K",
                 delta_color=profit_delta)
    with col5:
        st.metric("📊 Market Share", f"{state['metrics'].market_share*100:.1f}%")
    with col6:
        st.metric("🏆 Valuation", f"${state['metrics'].valuation/1_000_000:.2f}M")
    
    # Show last event if exists
    if state['last_event']:
        event = state['last_event']
        if event.effect_type == 'positive':
            st.success(f"**{event.title}** - {event.description}")
        elif event.effect_type == 'negative':
            st.error(f"**{event.title}** - {event.description}")
        else:
            st.info(f"**{event.title}** - {event.description}")
    
    st.markdown("---")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💼 Operations", "🏢 Competitors", "📈 History"])
    
    with tab1:
        # Current quarter summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current Quarter Summary")
            st.write(f"**Units Sold:** {state['metrics'].units_sold:,}")
            st.write(f"**Unit Cost:** ${state['metrics'].unit_cost:.2f}")
            st.write(f"**Gross Profit:** ${state['metrics'].gross_profit:,.0f}")
            st.write(f"**Operating Expenses:** ${state['metrics'].operating_expenses:,.0f}")
            st.write(f"**Technology Level:** {state['metrics'].tech_level:.2f}")
            st.write(f"**Cumulative Production:** {state['metrics'].cumulative_production:,} units")
        
        with col2:
            st.subheader("Funding Summary")
            st.write(f"**Total Raised:** ${state['metrics'].total_funding_raised:,.0f}")
            st.write(f"**Equity Given:** {state['metrics'].equity_given*100:.1f}%")
            st.write(f"**Remaining Equity:** {(1-state['metrics'].equity_given)*100:.1f}%")
            
            st.subheader("Team")
            for dept_name, dept in state['departments'].items():
                st.write(f"**{dept_name}:** {dept.headcount} (${dept.headcount*dept.salary_per_person:,.0f}/qtr)")
        
        # Charts
        if state['history']:
            st.plotly_chart(create_financial_chart(state['history']), use_container_width=True)
    
    with tab2:
        st.subheader("Quarterly Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Production & Pricing")
            current_price = state['metrics'].units_sold * company.price if state['metrics'].quarter > 0 else 450
            price = st.slider("Unit Price ($)", 200, 800, int(company.price), 10,
                             help="Set your selling price per unit")
            
            production = st.number_input("Planned Production (units)", 0, 20000, 
                                        company.planned_production, 100,
                                        help="How many units to produce this quarter")
            
            st.write(f"**Current Unit Cost:** ${state['metrics'].unit_cost:.2f}")
            margin = ((price - state['metrics'].unit_cost) / price * 100) if price > 0 else 0
            st.write(f"**Gross Margin:** {margin:.1f}%")
        
        with col2:
            st.markdown("#### Investment")
            marketing = st.number_input("Marketing Spend ($)", 0, 1_000_000, 
                                       company.marketing_spend, 10_000,
                                       help="Marketing drives demand")
            
            rd = st.number_input("R&D Spend ($)", 0, 1_000_000, 
                                company.rd_spend, 10_000,
                                help="R&D improves technology level")
            
            quarterly_burn = sum(d.headcount * d.salary_per_person 
                               for d in state['departments'].values())
            total_expenses = quarterly_burn + marketing + rd + 50_000
            st.warning(f"**Estimated Quarterly Burn:** ${total_expenses:,.0f}")
    
    with tab3:
        st.subheader("Competitor Analysis")
        
        if state['competitors']:
            st.plotly_chart(create_competitor_chart(state['competitors']), use_container_width=True)
            
            st.markdown("#### Competitor Details")
            for comp in state['competitors']:
                if comp.is_active:
                    with st.expander(f"🏢 {comp.name}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Tech Level", f"{comp.tech_level:.2f}")
                        with col2:
                            st.metric("Market Share", f"{comp.market_share*100:.1f}%")
                        with col3:
                            st.metric("Price", f"${comp.price:.0f}")
    
    with tab4:
        st.subheader("Historical Performance")
        
        if state['history']:
            df = pd.DataFrame([
                {
                    'Quarter': m.quarter,
                    'Cash ($M)': m.cash / 1_000_000,
                    'Revenue ($K)': m.revenue / 1_000,
                    'Net Income ($K)': m.net_income / 1_000,
                    'Units Sold': m.units_sold,
                    'Market Share (%)': m.market_share * 100,
                    'Tech Level': m.tech_level,
                    'Unit Cost ($)': m.unit_cost,
                    'Valuation ($M)': m.valuation / 1_000_000
                }
                for m in state['history']
            ])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No historical data yet. Complete your first quarter to see results.")
    
    st.markdown("---")
    
    # Sidebar for decisions
    with st.sidebar:
        st.header("🎮 Controls")
        
        st.subheader("💰 Raise Funding")
        funding_type = st.selectbox(
            "Funding Source",
            options=["Angel Investment", "VC Series A", "VC Series B", "Government Grant", "Debt Financing"],
            help="Different funding sources have different terms"
        )
        
        if st.button("💵 Raise Funding", use_container_width=True):
            # Map display names to enum values
            funding_map = {
                "Angel Investment": FundingType.ANGEL,
                "VC Series A": FundingType.VC_A,
                "VC Series B": FundingType.VC_B,
                "Government Grant": FundingType.GRANT,
                "Debt Financing": FundingType.DEBT
            }
            ft = funding_map[funding_type]
            result = company.raise_funding(ft)
            if result['success']:
                st.success(f"{result['message']} (Dilution: {result['dilution']*100:.1f}%)")
                st.rerun()
            else:
                st.error(result['message'])
        
        st.markdown("---")
        st.subheader("👥 Team Management")
        
        dept_name = st.selectbox("Department", list(state['departments'].keys()))
        hire_fire = st.number_input("Hire (+) / Fire (-)", -10, 10, 0, 1)
        
        if st.button("Apply Change", use_container_width=True):
            result = company.hire_fire(dept_name, hire_fire)
            if result['success']:
                st.success(result['message'])
                st.rerun()
            else:
                st.error(result['message'])
        
        st.markdown("---")
        
        # Show current decisions
        st.subheader("Current Quarter Settings")
        st.write(f"Price: ${price}")
        st.write(f"Production: {production:,} units")
        st.write(f"Marketing: ${marketing:,}")
        st.write(f"R&D: ${rd:,}")
        
        st.markdown("---")
        
        # Advance quarter button
        if st.button("➡️ Advance Quarter", type="primary", use_container_width=True):
            decisions = {
                'price': price,
                'production': production,
                'marketing': marketing,
                'rd': rd
            }
            
            result = company.advance_quarter(decisions)
            st.rerun()
        
        st.markdown("---")
        
        if st.button("🔄 Reset Game", use_container_width=True):
            st.session_state.game_initialized = False
            st.session_state.company = None
            st.session_state.tech_selected = None
            st.rerun()


def main():
    """Main application entry point"""
    initialize_game()
    
    if not st.session_state.game_initialized:
        render_game_start()
    else:
        company = st.session_state.company
        if company.game_over:
            render_game_over()
        else:
            render_main_game()


if __name__ == "__main__":
    main()
