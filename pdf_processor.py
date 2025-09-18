import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import google.generativeai as genai
import concurrent.futures
import threading

# Configure logging
import time
from datetime import datetime

def setup_logging(section_code: str = None):
    """Set up logging to both file and console."""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Generate timestamp for log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if section_code:
        log_filename = f"processing_{section_code}_{timestamp}.log"
    else:
        log_filename = f"processing_{timestamp}.log"

    log_path = log_dir / log_filename

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_path}")
    return logger, log_path

# Initialize basic logger (will be reconfigured when processing starts)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, api_key: str):
        """Initialize PDF processor with Gemini API key."""
        genai.configure(api_key=api_key)
        self.model_id = "gemini-2.5-flash"

    def upload_pdf_to_gemini(self, pdf_path: str) -> Optional[str]:
        """
        Upload a PDF file to Gemini API.

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            Optional[str]: File ID if successful, None if failed
        """
        try:
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return None

            logger.info(f"Uploading PDF: {pdf_path}")

            # Upload file to Gemini
            upload_response = genai.upload_file(pdf_path)

            file_id = upload_response.name
            logger.info(f"PDF uploaded successfully. File ID: {file_id}")
            return file_id

        except Exception as e:
            logger.error(f"Error uploading PDF {pdf_path}: {str(e)}")
            return None

    def delete_file_from_gemini(self, file_id: str) -> bool:
        """
        Delete a file from Gemini API.

        Args:
            file_id (str): File ID to delete

        Returns:
            bool: True if successful, False if failed
        """
        try:
            logger.info(f"Deleting file from Gemini: {file_id}")
            genai.delete_file(file_id)
            logger.info(f"File deleted successfully: {file_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            return False

    def generate_prompt(self, section_code: str, sequence_id: int) -> str:
        """
        Generate the processing prompt based on prompt.md requirements.

        Args:
            section_code (str): Project section code (e.g., "3.1")
            sequence_id (int): Sequential ID for the paper

        Returns:
            str: Complete prompt for Gemini API
        """
        # Read the prompt template from prompt.md
        prompt_path = Path("prompt.md")
        if not prompt_path.exists():
            logger.error("prompt.md file not found")
            return ""

        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()

        # Add specific instructions for this paper
        paper_prompt = f"""
Section Code: {section_code}
Sequence ID: {sequence_id}

{prompt_template}

Please analyze the uploaded PDF and generate a JSON response following the exact schema provided above.
"""

        return paper_prompt

    def process_pdf_with_gemini(self, file_id: str, section_code: str, sequence_id: int) -> Optional[Dict[Any, Any]]:
        """
        Process uploaded PDF with Gemini API to generate structured JSON.

        Args:
            file_id (str): Gemini file ID
            section_code (str): Project section code
            sequence_id (int): Sequential ID for the paper

        Returns:
            Optional[Dict]: Parsed JSON response if successful, None if failed
        """
        try:
            logger.info(f"Processing PDF with Gemini. File ID: {file_id}")

            # Generate the prompt
            prompt = self.generate_prompt(section_code, sequence_id)

            # Get the uploaded file
            uploaded_file = genai.get_file(file_id)

            # Create the model
            model = genai.GenerativeModel(self.model_id)

            # Send request to Gemini
            response = model.generate_content([prompt, uploaded_file])

            # Extract text response
            if not response.text:
                logger.error("No response content from Gemini")
                return None

            response_text = response.text
            logger.info("Received response from Gemini")

            # Parse JSON response - handle markdown code blocks
            try:
                # Remove markdown code blocks if present
                if response_text.strip().startswith('```json'):
                    # Extract JSON from markdown code block
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        json_text = response_text[start_idx:end_idx+1]
                    else:
                        json_text = response_text
                elif response_text.strip().startswith('```'):
                    # Generic code block
                    lines = response_text.strip().split('\n')
                    json_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
                else:
                    json_text = response_text

                json_data = json.loads(json_text)
                logger.info("Successfully parsed JSON response")
                return json_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response text: {response_text[:500]}...")
                return None

        except Exception as e:
            logger.error(f"Error processing PDF with Gemini: {str(e)}")
            return None

    def save_json_output(self, json_data: Dict[Any, Any], paper_id: str, section_code: str) -> bool:
        """
        Save JSON data to output file in section-specific directory.

        Args:
            json_data (Dict): JSON data to save
            paper_id (str): Paper ID for filename
            section_code (str): Section code for directory structure

        Returns:
            bool: True if successful, False if failed
        """
        try:
            # Create section-specific output directory
            output_dir = Path("data/output") / section_code
            output_dir.mkdir(parents=True, exist_ok=True)

            output_path = output_dir / f"{paper_id}.json"

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            logger.info(f"JSON saved to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving JSON for {paper_id}: {str(e)}")
            return False

    def process_single_pdf(self, pdf_path: str, section_code: str, sequence_id: int) -> bool:
        """
        Complete workflow: upload PDF → process with Gemini → save JSON → delete from cloud.

        Args:
            pdf_path (str): Path to PDF file
            section_code (str): Project section code
            sequence_id (int): Sequential ID for the paper

        Returns:
            bool: True if successful, False if failed
        """
        file_id = None
        try:
            # Step 1: Upload PDF
            file_id = self.upload_pdf_to_gemini(pdf_path)
            if not file_id:
                return False

            # Step 2: Process with Gemini
            json_data = self.process_pdf_with_gemini(file_id, section_code, sequence_id)
            if not json_data:
                return False

            # Step 3: Generate paper ID and save JSON
            paper_id = f"{section_code}-{sequence_id:03d}"
            success = self.save_json_output(json_data, paper_id, section_code)

            return success

        except Exception as e:
            logger.error(f"Error in complete PDF processing workflow: {str(e)}")
            return False

        finally:
            # Step 4: Always try to delete the file from cloud
            if file_id:
                self.delete_file_from_gemini(file_id)

    def process_pdfs_in_directory(self, directory_path: str, section_code: str) -> Dict[str, Any]:
        """
        Process all PDFs in a directory sequentially with comprehensive logging.

        Args:
            directory_path (str): Path to directory containing PDFs
            section_code (str): Project section code (e.g., "3.1")

        Returns:
            Dict[str, Any]: Processing results with statistics
        """
        # Set up logging for this processing session
        global logger
        logger, log_path = setup_logging(section_code)
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return {"success": False, "error": "Directory not found"}

        # Get all PDF files and sort them for consistent ordering
        pdf_files = sorted(list(directory.glob("*.pdf")), key=lambda x: x.name.lower())
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return {"success": True, "processed": 0, "failed": 0, "files": []}

        # Log the processing order
        logger.info("📋 Processing order:")
        for idx, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"  {idx:2d}. {pdf_file.name}")
        logger.info("")

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        results = {
            "success": True,
            "total_files": len(pdf_files),
            "processed": 0,
            "failed": 0,
            "files": []
        }

        # Process each PDF
        for idx, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"Processing file {idx}/{len(pdf_files)}: {pdf_file.name}")

            file_result = {
                "filename": pdf_file.name,
                "sequence_id": idx,
                "paper_id": f"{section_code}-{idx:03d}",
                "success": False,
                "error": None
            }

            try:
                success = self.process_single_pdf(str(pdf_file), section_code, idx)
                if success:
                    file_result["success"] = True
                    results["processed"] += 1
                    logger.info(f"✅ Successfully processed: {pdf_file.name}")
                else:
                    file_result["error"] = "Processing failed"
                    results["failed"] += 1
                    logger.error(f"❌ Failed to process: {pdf_file.name}")

            except Exception as e:
                file_result["error"] = str(e)
                results["failed"] += 1
                logger.error(f"❌ Error processing {pdf_file.name}: {str(e)}")

            results["files"].append(file_result)

            # Reduced delay between files (was 5 seconds)
            if idx < len(pdf_files):  # Don't wait after the last file
                logger.info("Waiting 1 second before next file...")
                import time
                time.sleep(1)

        # Final summary
        logger.info(f"""
        📊 Processing Complete:
        - Total files: {results['total_files']}
        - Successfully processed: {results['processed']}
        - Failed: {results['failed']}
        - Success rate: {(results['processed']/results['total_files']*100):.1f}%
        """)

        # Save processing summary to log file
        self.save_processing_summary(results, section_code)

        return results

    def save_processing_summary(self, results: Dict[str, Any], section_code: str):
        """Save processing summary and progress to a file for resume capability."""
        summary_dir = Path("logs") / "summaries"
        summary_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = summary_dir / f"summary_{section_code}_{timestamp}.json"

        summary_data = {
            "timestamp": timestamp,
            "section_code": section_code,
            "results": results,
            "processed_files": [f["filename"] for f in results.get("files", []) if f.get("success")],
            "failed_files": [f["filename"] for f in results.get("files", []) if not f.get("success")],
            "next_sequence_id": results.get("processed", 0) + 1
        }

        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Processing summary saved to: {summary_file}")
        except Exception as e:
            logger.error(f"Failed to save processing summary: {str(e)}")

    def get_already_processed_files(self, section_code: str) -> set:
        """Check which files have already been processed in this section."""
        output_dir = Path("data/output") / section_code
        processed_files = set()

        if output_dir.exists():
            for json_file in output_dir.glob("*.json"):
                # Extract sequence number from filename like "3.1-001.json"
                try:
                    parts = json_file.stem.split('-')
                    if len(parts) == 2:
                        sequence_num = int(parts[1])
                        processed_files.add(sequence_num)
                except (ValueError, IndexError):
                    continue

        logger.info(f"Found {len(processed_files)} already processed files in section {section_code}")
        return processed_files

    def process_pdfs_with_resume(self, directory_path: str, section_code: str, start_from: int = 1) -> Dict[str, Any]:
        """
        Process PDFs with resume capability.

        Args:
            directory_path (str): Path to directory containing PDFs
            section_code (str): Project section code
            start_from (int): Sequence number to start from

        Returns:
            Dict[str, Any]: Processing results with statistics
        """
        # Set up logging
        global logger
        logger, _ = setup_logging(section_code)

        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return {"success": False, "error": "Directory not found"}

        # Get all PDF files and sort them for consistent ordering
        pdf_files = sorted(list(directory.glob("*.pdf")), key=lambda x: x.name.lower())
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return {"success": True, "processed": 0, "failed": 0, "files": []}

        # Log the processing order
        logger.info("📋 Processing order:")
        for idx, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"  {idx:2d}. {pdf_file.name}")
        logger.info("")

        # Check already processed files
        already_processed = self.get_already_processed_files(section_code)

        logger.info(f"Found {len(pdf_files)} total PDF files")
        logger.info(f"Starting from sequence {start_from}")

        results = {
            "success": True,
            "total_files": len(pdf_files),
            "processed": 0,
            "failed": 0,
            "skipped": 0,
            "files": []
        }

        # Process each PDF
        for idx, pdf_file in enumerate(pdf_files, 1):
            if idx < start_from:
                logger.info(f"Skipping file {idx}/{len(pdf_files)}: {pdf_file.name} (before start point)")
                results["skipped"] += 1
                continue

            if idx in already_processed:
                logger.info(f"Skipping file {idx}/{len(pdf_files)}: {pdf_file.name} (already processed)")
                results["skipped"] += 1
                continue

            logger.info(f"Processing file {idx}/{len(pdf_files)}: {pdf_file.name}")

            file_result = {
                "filename": pdf_file.name,
                "sequence_id": idx,
                "paper_id": f"{section_code}-{idx:03d}",
                "success": False,
                "error": None,
                "start_time": datetime.now().isoformat(),
                "end_time": None
            }

            try:
                success = self.process_single_pdf(str(pdf_file), section_code, idx)
                file_result["end_time"] = datetime.now().isoformat()

                if success:
                    file_result["success"] = True
                    results["processed"] += 1
                    logger.info(f"✅ Successfully processed: {pdf_file.name}")
                else:
                    file_result["error"] = "Processing failed"
                    results["failed"] += 1
                    logger.error(f"❌ Failed to process: {pdf_file.name}")

            except Exception as e:
                file_result["error"] = str(e)
                file_result["end_time"] = datetime.now().isoformat()
                results["failed"] += 1
                logger.error(f"❌ Error processing {pdf_file.name}: {str(e)}")

            results["files"].append(file_result)

            # Save intermediate progress
            if idx % 5 == 0:  # Save progress every 5 files
                logger.info(f"💾 Checkpoint: Processed {results['processed']}/{len(pdf_files)} files")

            # Reduced delay between files (was 5 seconds)
            if idx < len(pdf_files):
                logger.info("Waiting 1 second before next file...")
                import time
                time.sleep(1)

        # Final summary
        logger.info(f"""
        📊 Processing Complete:
        - Total files: {results['total_files']}
        - Successfully processed: {results['processed']}
        - Failed: {results['failed']}
        - Skipped: {results['skipped']}
        - Success rate: {(results['processed']/(results['total_files']-results['skipped'])*100):.1f}%
        """)

        self.save_processing_summary(results, section_code)
        return results

    def process_pdfs_in_directory_with_resume(self, directory_path: str, section_code: str, start_from: int = 1) -> Dict[str, Any]:
        """Process PDFs starting from a specific sequence number."""
        # Set up logging
        global logger
        logger, _ = setup_logging(section_code)

        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return {"success": False, "error": "Directory not found"}

        # Check what's already processed
        output_dir = Path("data/output") / section_code
        processed_files = set()
        if output_dir.exists():
            for json_file in output_dir.glob("*.json"):
                processed_files.add(json_file.stem)  # e.g., "3.1-001"

        logger.info(f"Found {len(processed_files)} already processed files: {sorted(processed_files)}")

        # Get all PDF files and sort them for consistent ordering
        pdf_files = sorted(list(directory.glob("*.pdf")), key=lambda x: x.name.lower())
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return {"success": True, "processed": 0, "failed": 0, "files": []}

        # Log the processing order
        logger.info("📋 Processing order:")
        for idx, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"  {idx:2d}. {pdf_file.name}")
        logger.info("")

        logger.info(f"Found {len(pdf_files)} total PDF files")
        logger.info(f"Starting from sequence {start_from}")

        results = {
            "success": True,
            "total_files": len(pdf_files),
            "processed": 0,
            "failed": 0,
            "skipped": 0,
            "files": []
        }

        # Process each PDF, skipping already processed ones
        for idx, pdf_file in enumerate(pdf_files, start_from):
            paper_id = f"{section_code}-{idx:03d}"

            # Skip if already processed
            if paper_id in processed_files:
                logger.info(f"Skipping file {idx}: {pdf_file.name} (already processed as {paper_id})")
                results["skipped"] += 1
                continue

            # Skip if before start point
            if idx < start_from:
                logger.info(f"Skipping file {idx}: {pdf_file.name} (before start point)")
                results["skipped"] += 1
                continue

            logger.info(f"Processing file {idx}/{len(pdf_files) + start_from - 1}: {pdf_file.name}")

            file_result = {
                "filename": pdf_file.name,
                "sequence_id": idx,
                "paper_id": paper_id,
                "success": False,
                "error": None,
                "start_time": datetime.now().isoformat(),
                "end_time": None
            }

            try:
                success = self.process_single_pdf(str(pdf_file), section_code, idx)
                file_result["end_time"] = datetime.now().isoformat()

                if success:
                    file_result["success"] = True
                    results["processed"] += 1
                    logger.info(f"✅ Successfully processed: {pdf_file.name}")
                else:
                    file_result["error"] = "Processing failed"
                    results["failed"] += 1
                    logger.error(f"❌ Failed to process: {pdf_file.name}")

            except Exception as e:
                file_result["error"] = str(e)
                file_result["end_time"] = datetime.now().isoformat()
                results["failed"] += 1
                logger.error(f"❌ Error processing {pdf_file.name}: {str(e)}")

            results["files"].append(file_result)

            # Save intermediate progress every 5 files
            if (idx - start_from + 1) % 5 == 0:
                logger.info(f"💾 Checkpoint: Processed {results['processed']}/{len(pdf_files)} files")

            # Reduced delay between files (was 5 seconds)
            if idx < len(pdf_files) + start_from - 1:
                logger.info("Waiting 1 second before next file...")
                import time
                time.sleep(1)

        # Final summary
        total_attempted = results['processed'] + results['failed']
        success_rate = (results['processed'] / total_attempted * 100) if total_attempted > 0 else 0

        logger.info(f"""
        📊 Processing Complete:
        - Total files: {results['total_files']}
        - Successfully processed: {results['processed']}
        - Failed: {results['failed']}
        - Skipped: {results['skipped']}
        - Success rate: {success_rate:.1f}%
        """)

        self.save_processing_summary(results, section_code)
        return results

    def process_single_pdf_with_logging(self, pdf_file: Path, section_code: str, sequence_id: int) -> Dict[str, Any]:
        """
        Thread-safe wrapper for processing a single PDF with detailed logging.
        """
        file_result = {
            "filename": pdf_file.name,
            "sequence_id": sequence_id,
            "paper_id": f"{section_code}-{sequence_id:03d}",
            "success": False,
            "error": None,
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }

        try:
            logger.info(f"🔄 [{sequence_id:03d}] Starting: {pdf_file.name}")
            success = self.process_single_pdf(str(pdf_file), section_code, sequence_id)
            file_result["end_time"] = datetime.now().isoformat()

            if success:
                file_result["success"] = True
                logger.info(f"✅ [{sequence_id:03d}] Completed: {pdf_file.name}")
            else:
                file_result["error"] = "Processing failed"
                logger.error(f"❌ [{sequence_id:03d}] Failed: {pdf_file.name}")

        except Exception as e:
            file_result["error"] = str(e)
            file_result["end_time"] = datetime.now().isoformat()
            logger.error(f"❌ [{sequence_id:03d}] Error in {pdf_file.name}: {str(e)}")

        return file_result

    def process_pdfs_parallel(self, directory_path: str, section_code: str, max_workers: int = 3) -> Dict[str, Any]:
        """
        Process PDFs in parallel using ThreadPoolExecutor.

        Args:
            directory_path (str): Path to directory containing PDFs
            section_code (str): Project section code
            max_workers (int): Maximum number of parallel workers (default: 3)
        """
        # Set up logging
        global logger
        logger, _ = setup_logging(section_code)

        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return {"success": False, "error": "Directory not found"}

        # Get all PDF files and sort them for consistent ordering
        pdf_files = sorted(list(directory.glob("*.pdf")), key=lambda x: x.name.lower())
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return {"success": True, "processed": 0, "failed": 0, "files": []}

        # Log the processing order
        logger.info("📋 Processing order (PARALLEL MODE):")
        for idx, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"  {idx:2d}. {pdf_file.name}")
        logger.info("")

        logger.info(f"🚀 Starting parallel processing with {max_workers} workers")
        logger.info(f"📊 Found {len(pdf_files)} PDF files to process")

        results = {
            "success": True,
            "total_files": len(pdf_files),
            "processed": 0,
            "failed": 0,
            "files": [],
            "parallel_workers": max_workers
        }

        # Process PDFs in parallel
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_pdf = {}
                for idx, pdf_file in enumerate(pdf_files, 1):
                    future = executor.submit(
                        self.process_single_pdf_with_logging,
                        pdf_file,
                        section_code,
                        idx
                    )
                    future_to_pdf[future] = (pdf_file, idx)

                # Collect results as they complete
                completed = 0
                for future in concurrent.futures.as_completed(future_to_pdf):
                    pdf_file, idx = future_to_pdf[future]
                    completed += 1

                    try:
                        file_result = future.result()
                        results["files"].append(file_result)

                        if file_result["success"]:
                            results["processed"] += 1
                        else:
                            results["failed"] += 1

                        # Progress update
                        progress = (completed / len(pdf_files)) * 100
                        logger.info(f"📈 Progress: {completed}/{len(pdf_files)} ({progress:.1f}%) - Last completed: {pdf_file.name}")

                    except Exception as e:
                        results["failed"] += 1
                        logger.error(f"❌ Exception in parallel processing for {pdf_file.name}: {str(e)}")

        except Exception as e:
            logger.error(f"❌ Critical error in parallel processing: {str(e)}")
            results["success"] = False
            return results

        # Final summary
        logger.info(f"""
        🎉 Parallel Processing Complete:
        - Total files: {results['total_files']}
        - Successfully processed: {results['processed']}
        - Failed: {results['failed']}
        - Success rate: {(results['processed']/results['total_files']*100):.1f}%
        - Workers used: {max_workers}
        """)

        self.save_processing_summary(results, section_code)
        return results