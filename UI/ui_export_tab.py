import streamlit as st
import pandas as pd
import io
from datetime import datetime
from typing import Any, Optional


class ExportTabUI:
    """
    Export Tab UI component for the Job Portal Dashboard.
    
    This class handles all data export functionality including:
    - CSV file downloads
    - Excel file downloads
    - Local file saving
    - Data filtering and export options
    - Export analytics and reporting
    """
    
    def __init__(self):
        """Initialize the Export Tab UI component."""
        pass
    
    def render(self, jobs_df: pd.DataFrame, job_service: Any) -> None:
        """
        Main render method for the export tab.
        
        Args:
            jobs_df: DataFrame containing job data
            job_service: Job service instance for additional functionality
        """
        st.subheader("💾 Export Data")
        
        if jobs_df.empty:
            st.warning("No job data available for export.")
            return
        
        # Display export summary
        self._render_export_summary(jobs_df)
        
        # Export options
        self._render_export_options(jobs_df, job_service)
        
        # Advanced export features
        self._render_advanced_export_options(jobs_df, job_service)
        
        # Export history and analytics
        self._render_export_analytics(jobs_df)
    
    def _render_export_summary(self, jobs_df: pd.DataFrame) -> None:
        """Render summary information about the data to be exported."""
        st.markdown("### 📊 Export Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_jobs = len(jobs_df)
            st.metric("Total Jobs", total_jobs)
        
        with col2:
            total_columns = len(jobs_df.columns)
            st.metric("Total Columns", total_columns)
        
        with col3:
            memory_usage = jobs_df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
            st.metric("Data Size", f"{memory_usage:.2f} MB")
        
        with col4:
            non_null_percentage = (jobs_df.count().sum() / (len(jobs_df) * len(jobs_df.columns)) * 100)
            st.metric("Data Completeness", f"{non_null_percentage:.1f}%")
    
    def _render_export_options(self, jobs_df: pd.DataFrame, job_service: Any) -> None:
        """Render the main export options (CSV, Excel, Local)."""
        st.markdown("### 📥 Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self._render_csv_download(jobs_df)
        
        with col2:
            self._render_excel_download(jobs_df)
        
        with col3:
            self._render_local_save(jobs_df, job_service)
    
    def _render_csv_download(self, jobs_df: pd.DataFrame) -> None:
        """Render CSV download button."""
        csv_data = jobs_df.to_csv(index=False)
        filename = f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
            help="Download the complete dataset as a CSV file"
        )
        
        # Display CSV info
        csv_size = len(csv_data.encode('utf-8')) / 1024 / 1024  # MB
        st.caption(f"File size: ~{csv_size:.2f} MB")
    
    def _render_excel_download(self, jobs_df: pd.DataFrame) -> None:
        """Render Excel download button."""
        try:
            buffer = io.BytesIO()
            filename = f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Main jobs sheet
                jobs_df.to_excel(writer, sheet_name='Jobs', index=False)
                
                # Summary sheet
                summary_df = self._create_summary_sheet(jobs_df)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Column info sheet
                column_info_df = self._create_column_info_sheet(jobs_df)
                column_info_df.to_excel(writer, sheet_name='Column_Info', index=False)
            
            st.download_button(
                label="📊 Download as Excel",
                data=buffer.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Download as Excel with multiple sheets including summary and analysis"
            )
            
            # Display Excel info
            excel_size = len(buffer.getvalue()) / 1024 / 1024  # MB
            st.caption(f"File size: ~{excel_size:.2f} MB")
            st.caption("Includes: Jobs, Summary, Column Info sheets")
            
        except ImportError:
            st.error("❌ Excel export unavailable")
            st.info("💡 Install openpyxl for Excel export: `pip install openpyxl`")
            
            # Alternative: show install button
            if st.button("🔧 Install openpyxl", use_container_width=True):
                st.code("pip install openpyxl", language="bash")
    
    def _render_local_save(self, jobs_df: pd.DataFrame, job_service: Any) -> None:
        """Render local save option."""
        if st.button("💾 Save to Local CSV", use_container_width=True, help="Save file to the application's local directory"):
            try:
                filename = f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                job_service.save_jobs_to_csv(jobs_df, filename)
                st.success(f"✅ Data saved to {filename}")
                st.info(f"📁 File saved in the application directory")
            except Exception as e:
                st.error(f"❌ Error saving file: {str(e)}")
    
    def _render_advanced_export_options(self, jobs_df: pd.DataFrame, job_service: Any) -> None:
        """Render advanced export options with filtering and customization."""
        st.markdown("### ⚙️ Advanced Export Options")
        
        with st.expander("🔧 Customize Export", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Column selection
                st.markdown("**Select Columns to Export:**")
                available_columns = jobs_df.columns.tolist()
                selected_columns = st.multiselect(
                    "Choose columns",
                    available_columns,
                    default=available_columns,
                    key="export_columns"
                )
            
            with col2:
                # Row filtering options
                st.markdown("**Filter Rows:**")
                
                # Sample size option
                max_rows = st.number_input(
                    "Maximum rows to export (0 = all)",
                    min_value=0,
                    max_value=len(jobs_df),
                    value=0,
                    step=100,
                    key="export_max_rows"
                )
                
                # Filter by date if available
                if 'date_posted' in jobs_df.columns:
                    filter_by_date = st.checkbox("Filter by date range", key="export_date_filter")
                    if filter_by_date:
                        try:
                            jobs_df_temp = jobs_df.copy()
                            jobs_df_temp['date_posted'] = pd.to_datetime(jobs_df_temp['date_posted'], errors='coerce')
                            valid_dates = jobs_df_temp['date_posted'].dropna()
                            
                            if len(valid_dates) > 0:
                                min_date = valid_dates.min().date()
                                max_date = valid_dates.max().date()
                                
                                date_range = st.date_input(
                                    "Select date range",
                                    value=(min_date, max_date),
                                    min_value=min_date,
                                    max_value=max_date,
                                    key="export_date_range"
                                )
                        except:
                            st.info("Date filtering not available - invalid date format")
            
            # Generate filtered dataset
            if selected_columns:
                filtered_df = self._apply_export_filters(jobs_df, selected_columns, max_rows)
                
                st.markdown(f"**Filtered Dataset: {len(filtered_df)} rows, {len(selected_columns)} columns**")
                
                # Custom export buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📄 Export Filtered CSV", use_container_width=True):
                        csv_data = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="⬇️ Download Filtered CSV",
                            data=csv_data,
                            file_name=f"jobs_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            key="download_filtered_csv"
                        )
                
                with col2:
                    if st.button("📊 Export Filtered Excel", use_container_width=True):
                        try:
                            buffer = io.BytesIO()
                            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                filtered_df.to_excel(writer, sheet_name='Filtered_Jobs', index=False)
                            
                            st.download_button(
                                label="⬇️ Download Filtered Excel",
                                data=buffer.getvalue(),
                                file_name=f"jobs_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="download_filtered_excel"
                            )
                        except ImportError:
                            st.error("Excel export not available")
                
                with col3:
                    if st.button("👁️ Preview Filtered Data", use_container_width=True):
                        st.dataframe(filtered_df.head(10), use_container_width=True)
                        if len(filtered_df) > 10:
                            st.caption(f"Showing first 10 rows of {len(filtered_df)} total rows")
    
    def _render_export_analytics(self, jobs_df: pd.DataFrame) -> None:
        """Render export analytics and data insights."""
        with st.expander("📈 Data Insights", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Column Statistics:**")
                
                # Data types
                dtype_counts = jobs_df.dtypes.value_counts()
                st.write("Data Types:")
                for dtype, count in dtype_counts.items():
                    st.write(f"  • {dtype}: {count} columns")
                
                # Missing data analysis
                st.write("\n**Missing Data:**")
                missing_data = jobs_df.isnull().sum()
                missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
                
                if len(missing_data) > 0:
                    for col, missing_count in missing_data.head(5).items():
                        percentage = (missing_count / len(jobs_df)) * 100
                        st.write(f"  • {col}: {missing_count} ({percentage:.1f}%)")
                else:
                    st.write("  • No missing data found! 🎉")
            
            with col2:
                st.markdown("**🔍 Content Analysis:**")
                
                # Unique values analysis
                st.write("Unique Values (top columns):")
                unique_counts = jobs_df.nunique().sort_values(ascending=False)
                for col, unique_count in unique_counts.head(5).items():
                    percentage = (unique_count / len(jobs_df)) * 100
                    st.write(f"  • {col}: {unique_count} ({percentage:.1f}%)")
                
                # Memory usage by column
                st.write("\n**Memory Usage (top columns):**")
                memory_usage = jobs_df.memory_usage(deep=True).sort_values(ascending=False)
                for col, memory in memory_usage.head(5).items():
                    memory_mb = memory / 1024 / 1024
                    st.write(f"  • {col}: {memory_mb:.2f} MB")
    
    def _create_summary_sheet(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Create a summary sheet for Excel export."""
        summary_data = {
            'Metric': [
                'Total Jobs',
                'Total Columns',
                'Unique Companies',
                'Remote Jobs',
                'Jobs with Salary Info',
                'Average Salary (USD)',
                'Data Completeness (%)',
                'Export Date'
            ],
            'Value': [
                len(jobs_df),
                len(jobs_df.columns),
                jobs_df['company'].nunique() if 'company' in jobs_df.columns else 'N/A',
                len(jobs_df[jobs_df.get('is_remote', False) == True]) if 'is_remote' in jobs_df.columns else 'N/A',
                len(jobs_df[jobs_df.get('min_amount', 0) > 0]) if 'min_amount' in jobs_df.columns else 'N/A',
                f"${jobs_df[jobs_df.get('min_amount', 0) > 0]['min_amount'].mean():,.0f}" if 'min_amount' in jobs_df.columns and len(jobs_df[jobs_df.get('min_amount', 0) > 0]) > 0 else 'N/A',
                f"{(jobs_df.count().sum() / (len(jobs_df) * len(jobs_df.columns)) * 100):.1f}%",
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        
        return pd.DataFrame(summary_data)
    
    def _create_column_info_sheet(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """Create a column information sheet for Excel export."""
        column_info = []
        
        for col in jobs_df.columns:
            non_null_count = jobs_df[col].count()
            null_count = jobs_df[col].isnull().sum()
            null_percentage = (null_count / len(jobs_df)) * 100
            data_type = str(jobs_df[col].dtype)
            unique_count = jobs_df[col].nunique()
            
            column_info.append({
                'Column_Name': col,
                'Data_Type': data_type,
                'Non_Null_Count': non_null_count,
                'Null_Count': null_count,
                'Null_Percentage': f"{null_percentage:.1f}%",
                'Unique_Values': unique_count,
                'Sample_Value': str(jobs_df[col].dropna().iloc[0]) if non_null_count > 0 else 'N/A'
            })
        
        return pd.DataFrame(column_info)
    
    def _apply_export_filters(self, jobs_df: pd.DataFrame, selected_columns: list, max_rows: int) -> pd.DataFrame:
        """Apply export filters to the dataframe."""
        # Start with selected columns
        filtered_df = jobs_df[selected_columns].copy()
        
        # Apply row limit if specified
        if max_rows > 0 and max_rows < len(filtered_df):
            filtered_df = filtered_df.head(max_rows)
        
        return filtered_df
 