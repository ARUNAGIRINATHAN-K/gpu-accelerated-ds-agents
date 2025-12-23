"""Streamlit Dashboard for GPU-Accelerated Data Science Agents."""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gpu_pipeline import load_csv, Preprocessor, get_gpu_info
from agents import EDAAgent, ModelingAgent

# Page configuration
st.set_page_config(
    page_title="GPU-Accelerated Data Science Agents",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'eda_results' not in st.session_state:
    st.session_state.eda_results = None
if 'model_results' not in st.session_state:
    st.session_state.model_results = None

# Header
st.markdown('<div class="main-header">GPU-Accelerated Data Science Agents</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # GPU Info
    with st.expander("GPU Information", expanded=False):
        gpu_info = get_gpu_info()
        st.write(f"**Device**: {gpu_info['device']}")
        if gpu_info['gpu_available']:
            st.success(f"GPU Available: {gpu_info['device_name']}")
            st.write(f"**Memory**: {gpu_info['memory_total_gb']:.2f} GB")
        else:
            st.info("ℹRunning on CPU (GPU not available)")
    
    st.divider()
    
    # Workflow Selection
    st.subheader("🔧 Workflow")
    run_eda = st.checkbox("Run EDA Agent", value=True)
    run_modeling = st.checkbox("Run Modeling Agent", value=True)
    
    st.divider()
    
    # Agent Configuration
    with st.expander("Agent Settings"):
        st.subheader("Modeling")
        test_size = st.slider("Test Size", 0.1, 0.4, 0.2)
        algorithms = st.multiselect(
            "Algorithms",
            ["xgboost_gpu", "random_forest_gpu", "logistic_regression", "linear_regression"],
            default=["xgboost_gpu", "logistic_regression"]
        )

# Main content
tab1, tab2, tab3 = st.tabs(["Data Upload", "EDA Results", "Modeling"])

# Tab 1: Data Upload
with tab1:
    st.header("Upload Your Dataset")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file for analysis"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            with st.spinner("Loading data..."):
                df = pd.read_csv(uploaded_file)
                st.session_state.data = df
            
            st.success(f"Data loaded successfully: {df.shape[0]:,} rows × {df.shape[1]} columns")
            
            # Display preview
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Basic info
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Rows", f"{df.shape[0]:,}")
            with col_b:
                st.metric("Columns", df.shape[1])
            with col_c:
                st.metric("Missing Values", df.isnull().sum().sum())
            
            # Column info
            with st.expander("Column Information"):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null': df.count(),
                    'Null': df.isnull().sum(),
                    'Unique': df.nunique()
                })
                st.dataframe(col_info, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    st.divider()
    
    # Run Pipeline Button
    if st.session_state.data is not None:
        if st.button("Run Pipeline", type="primary", use_container_width=True):
            df = st.session_state.data.copy()
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Preprocessing
                status_text.text("⏳ Preprocessing data...")
                progress_bar.progress(10)
                
                preprocessor = Preprocessor(use_gpu=False)
                df_clean, _ = preprocessor.preprocess_pipeline(
                    df,
                    missing_strategy='mean',
                    encode_categoricals=False,
                    scale_method='standard',
                    remove_outliers=False
                )
                
                # EDA Agent
                if run_eda:
                    status_text.text("Running EDA Agent...")
                    progress_bar.progress(30)
                    
                    eda_agent = EDAAgent()
                    _, eda_report = eda_agent.run(df_clean)
                    st.session_state.eda_results = eda_report
                
                # Modeling
                if run_modeling:
                    status_text.text("Training models...")
                    progress_bar.progress(70)
                    
                    # Detect target column (last column by default)
                    target_col = df_clean.columns[-1]
                    
                    modeling_agent = ModelingAgent(config={
                        'algorithms': algorithms,
                        'test_size': test_size,
                    })
                    model_results, model_report = modeling_agent.run(
                        df_clean,
                        target_column=target_col
                    )
                    st.session_state.model_results = {
                        'results': model_results,
                        'report': model_report
                    }
                
                progress_bar.progress(100)
                status_text.text("Pipeline completed!")
                
                st.success("Pipeline completed successfully! Check the results in other tabs.")
                
            except Exception as e:
                st.error(f"Error running pipeline: {e}")
                import traceback
                st.code(traceback.format_exc())

# Tab 2: EDA Results
with tab2:
    st.header("🔍 Exploratory Data Analysis Results")
    
    if st.session_state.eda_results is not None:
        report = st.session_state.eda_results
        
        # Summary as KPI cards
        st.subheader("Dataset Overview")
        if st.session_state.data is not None:
            df = st.session_state.data
            
            # KPI Cards
            kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
            
            with kpi_col1:
                st.metric("Total Rows", f"{df.shape[0]:,}")
            with kpi_col2:
                st.metric("Total Columns", df.shape[1])
            with kpi_col3:
                st.metric("Numeric Features", len(df.select_dtypes(include=['number']).columns))
            with kpi_col4:
                st.metric("Categorical Features", len(df.select_dtypes(include=['object', 'category']).columns))
            with kpi_col5:
                total_missing = df.isnull().sum().sum()
                st.metric("Missing Values", f"{total_missing:,}")
            with kpi_col6:
                # Quick estimate of columns with outliers if EDA has run
                outlier_info = report.get('outliers', {})
                outlier_cols = len(outlier_info.get('columns_with_outliers', {}))
                st.metric("Outlier Columns", outlier_cols)
        
        st.divider()
        
        # Visualizations section
        st.subheader("Suggested Visualizations")
        
        if report.get('visualizations') and len(report['visualizations']) > 0:
            viz_cols = st.columns(3)
            for idx, viz in enumerate(report['visualizations']):
                with viz_cols[idx % 3]:
                    st.markdown(f"""
                    <div style='background-color: rgba(31, 119, 180, 0.1); padding: 1.25rem; margin: 0.5rem 0; border-radius: 0.5rem; text-align: center; border: 1px solid rgba(31, 119, 180, 0.2); height: 100px; display: flex; align-items: center; justify-content: center;'>
                        <div style='font-weight: 500;'>{viz}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No visualization suggestions available for this dataset")
        
        # Additional statistics
        st.subheader("Detailed Statistics")
        if st.session_state.data is not None:
            df = st.session_state.data
            numeric_df = df.select_dtypes(include=['number'])
            
            if not numeric_df.empty:
                st.write("**Numerical Features Statistics:**")
                st.dataframe(numeric_df.describe(), use_container_width=True)
            
            # Missing values breakdown
            missing = df.isnull().sum()
            missing_df = missing[missing > 0].to_frame('Missing Count')
            missing_df['Percentage'] = (missing_df['Missing Count'] / len(df) * 100).round(2)
            
            if not missing_df.empty:
                st.write("**Missing Values Breakdown:**")
                st.dataframe(missing_df, use_container_width=True)
        
    else:
        st.info("ℹRun the pipeline to see EDA results")
        st.markdown("""
        **What you'll get:**
        - Dataset overview and statistics
        - Suggested visualizations
        - Detailed statistical analysis
        """)



# Tab 3: Modeling
with tab3:
    st.header("Model Training Results")
    
    if st.session_state.model_results is not None:
        results = st.session_state.model_results['results']
        report = st.session_state.model_results['report']
        
        # Summary as 2x2 KPI cards
        st.subheader("Training Overview")
        
        # Determine task type once
        task_type = "Classification" if "classification" in report['summary'].lower() else "Regression"
        
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            best_model_name = results.get('best_model', 'None') or 'None'
            st.metric("Best Model", best_model_name)
        with row1_col2:
            st.metric("Task Type", task_type)
            
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            num_models = len(results['models'])
            st.metric("Models Trained", num_models)
        with row2_col2:
            # Try to get best score
            best_algo = results['best_model']
            if best_algo and best_algo in results['models'] and 'metrics' in results['models'][best_algo]:
                metrics = results['models'][best_algo].get('metrics', {})
                score_type = "Accuracy" if task_type == "Classification" else "R² Score"
                score_val = metrics.get('accuracy' if task_type == "Classification" else 'r2', 0)
                st.metric(f"Best {score_type}", f"{score_val:.4f}")
            else:
                st.metric("Best Score", "N/A")
        
        st.divider()
        
        # Best Model highlight
        best_model_display = results.get('best_model')
        if best_model_display:
            st.markdown(f"""
            <div style='background-color: #fff3cd; padding: 1.5rem; border-radius: 0.5rem; text-align: center; border: 2px solid #ffc107;'>
                <h2 style='margin: 0; color: #856404;'>🏆 Best Model: {best_model_display}</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No models were successfully trained. Check the 'Model Details' below or your dataset.")
        
        st.divider()
        
        # Model Comparison
        st.subheader("Model Performance Comparison")
        
        models_data = []
        training_errors = []
        for algo, result in results['models'].items():
            if 'error' not in result:
                metrics = result['metrics']
                models_data.append({
                    'Model': algo,
                    **metrics
                })
            else:
                training_errors.append({
                    'Model': algo,
                    'Error': result['error']
                })
        
        # Show errors if any
        if training_errors:
            with st.expander("⚠️ View Training Errors", expanded=not models_data):
                for err in training_errors:
                    st.error(f"**{err['Model']}**: {err['Error']}")
        
        if models_data:
            comparison_df = pd.DataFrame(models_data)
            
            # Display metrics table with styling
            st.dataframe(
                comparison_df.style.highlight_max(axis=0, subset=[col for col in comparison_df.columns if col != 'Model']),
                use_container_width=True
            )
            
            st.divider()
            
            # Visualize metrics
            st.subheader("Performance Metrics Visualization")
            
            if 'accuracy' in comparison_df.columns:
                # Classification metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Accuracy Comparison**")
                    st.bar_chart(comparison_df.set_index('Model')['accuracy'])
                
                with col2:
                    st.write("**F1 Score Comparison**")
                    if 'f1' in comparison_df.columns:
                        st.bar_chart(comparison_df.set_index('Model')['f1'])
                
                # Additional metrics
                if len(comparison_df.columns) > 3:
                    with st.expander("All Metrics Comparison"):
                        metric_cols = [col for col in comparison_df.columns if col != 'Model']
                        for metric in metric_cols:
                            st.write(f"**{metric.upper()}**")
                            st.bar_chart(comparison_df.set_index('Model')[metric])
            
            elif 'r2' in comparison_df.columns:
                # Regression metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**R² Score Comparison**")
                    st.bar_chart(comparison_df.set_index('Model')['r2'])
                
                with col2:
                    st.write("**RMSE Comparison** (lower is better)")
                    if 'rmse' in comparison_df.columns:
                        st.bar_chart(comparison_df.set_index('Model')['rmse'])
            
            st.divider()
            
            # Model details
            st.subheader("Model Details")
            
            selected_model = st.selectbox("Select model to view details:", comparison_df['Model'].tolist())
            
            if selected_model:
                model_metrics = comparison_df[comparison_df['Model'] == selected_model].iloc[0].to_dict()
                del model_metrics['Model']
                
                # Display metrics in columns
                metric_cols = st.columns(len(model_metrics))
                for idx, (metric_name, metric_value) in enumerate(model_metrics.items()):
                    with metric_cols[idx]:
                        st.metric(
                            metric_name.upper(),
                            f"{metric_value:.4f}",
                            help=f"{metric_name} score for {selected_model}"
                        )
        

    
    else:
        st.info("ℹRun the pipeline to see modeling results")
        st.markdown("""
        **What you'll get:**
        - Multiple model training (XGBoost, Random Forest, etc.)
        - Automatic model comparison
        - Best model selection
        - Performance metrics visualization
        - Detailed model analysis
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>GPU-Accelerated Autonomous Data Science Agents</p>
    <p>Built with RAPIDS, cuML, XGBoost GPU, and Streamlit</p>
</div>
""", unsafe_allow_html=True)
