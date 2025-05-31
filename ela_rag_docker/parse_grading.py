def parse_grading_response(raw_response):
    # Extract band scores from the response
    #task_response_score = re.search(r"Task Response\s*\|\s*(\d+)", raw_response)
    task_response_score = re.search(r"(?:Task Response|Task Achievement)\s*\|\s*(\d+)", raw_response)
    coherence_score = re.search(r"Coherence and Cohesion\s*\|\s*(\d+)", raw_response)
    lexical_score = re.search(r"Lexical Resource\s*\|\s*(\d+)", raw_response)
    grammar_score = re.search(r"Grammatical Range & Accuracy\s*\|\s*(\d+)", raw_response)
    overall_score = re.search(r"\*\*Overall Band Score\*\*\s*\|\s*\*\*(\d+)\*\*", raw_response)
    
    # task_response_feedback = re.search(
    # r"(?:^|\n)[#\d.\s]*\**(?:Task Response|Task Achievement)\**[:\-]?\s*(.*?)(?=\n[#\d.\s]*\**Coherence and Cohesion\**[:\-]?)",
    # raw_response, re.DOTALL)

    # coherence_feedback = re.search(
    # r"(?:^|\n)[#\d.\s]*\**Coherence and Cohesion\**[:\-]?\s*(.*?)(?=\n[#\d.\s]*\**Lexical Resource\**[:\-]?)",
    # raw_response, re.DOTALL)

    # lexical_feedback = re.search(
    # r"(?:^|\n)[#\d.\s]*\**Lexical Resource\**[:\-]?\s*(.*?)(?=(?:^|\n)[#\d.\s]*\**(?:Grammatical Range & Accuracy|Grammatical Range and Accuracy)\**|$)",
    # raw_response, re.DOTALL)

    # grammar_feedback = re.search(
    # r"(?:^|\n)[#\d.\s]*\**(?:Grammatical Range & Accuracy|Grammatical Range and Accuracy)\**[:\-]?\s*(.*?)(?=\n[#\d.\s]*\**Overall Band Score)",
    # raw_response, re.DOTALL)

    # overall_summary_feedback = re.search(
    # r"(?:^|\n)[#\d.\s]*\**Overall Band Score Summary\**[:\-]?\s*(.*?)(?=\n[#\d.\s]*\**Feedback\**[:\-]?)",
    # raw_response, re.DOTALL)

    # general_feedback = re.search(
    # r"(?:^|\n)[#\d.\s]*\**Feedback\**[:\-]?\s*(.*?)(?=\n[#\d.\s]*\**Scoring Table\**[:\-]?)",
    # raw_response, re.DOTALL)

    # task_response_feedback = re.search(
    # r"\*\*\s*1\.\s*Task Response\s*\*\*\s*(.*?)(?=\n\*\*\s*2\.\s*Coherence and Cohesion\s*\*\*)",
    # raw_response, re.DOTALL)
    # task_response_feedback = re.search( ###most recent working###
    # r"\*\*\s*1\.\s*(?:Task Response|Task Achievement)\s*\*\*\s*(.*?)(?=\n\*\*\s*2\.\s*Coherence and Cohesion\s*\*\*)",
    # raw_response, re.DOTALL | re.IGNORECASE)
    task_response_feedback = re.search(
    r"(?:^|\n)\s*(?:\*\*\s*)?(?:1\.\s*)?(?:\*\*)?\s*(Task Response|Task Achievement)\s*(?:\*\*)?\s*\n+(.*?)(?=\n\s*(?:\*\*\s*)?(?:2\.\s*)?(?:\*\*)?\s*Coherence and Cohesion)",
    raw_response,
    re.DOTALL | re.IGNORECASE
)

    coherence_feedback = re.search(
    r"\*\*\s*(?:2\.\s*)?Coherence and Cohesion\s*\*\*\s*(.*?)(?=\n\*\*\s*(?:3\.\s*)?Lexical Resource\s*\*\*)",
    raw_response, re.DOTALL)

    # lexical_feedback = re.search(
    # r"\*\*\s*3\.\s*Lexical Resource\s*\*\*\s*(.*?)(?=\n\*\*\s*4\.\s*Grammatical Range\s*&\s*Accuracy\s*\*\*)",
    # raw_response, re.DOTALL)
    lexical_feedback = re.search(
    r"\*\*\s*(?:3\.\s*)?Lexical Resource\s*\*\*\s*(.*?)(?=\n\*\*\s*(?:4\.\s*)?Grammatical Range\s*(?:&|and)\s*Accuracy\s*\*\*)",
    raw_response, re.DOTALL | re.IGNORECASE)

    # grammar_feedback = re.search(
    # r"\*\*\s*4\.\s*Grammatical Range\s*&\s*Accuracy\s*\*\*\s*(.*?)(?=\n\*\*\s*5\.\s*Overall Band Score Summary\s*\*\*)",
    # raw_response, re.DOTALL)
    grammar_feedback = re.search(
    r"\*\*\s*(?:4\.?)?\s*Grammatical Range\s*(?:&|and)\s*Accuracy\*\*\s*(.*?)(?=\n\*\*\s*(?:5\.?)?\s*Overall Band Score Summary\*\*)",
    raw_response, re.DOTALL | re.IGNORECASE)

    overall_summary_feedback = re.search(
    r"\*\*\s*(?:5\.\s*)?Overall Band Score Summary\s*\*\*\s*(.*?)(?=\n\*\*\s*(?:6\.\s*)?Feedback\s*\*\*)",
    raw_response, re.DOTALL)

    general_feedback = re.search(
    r"\*\*\s*(?:6\.\s*)?Feedback\s*\*\*\s*(.*?)(?=\n\*\*\s*(?:7\.\s*)?Scoring Table\s*\*\*)",
    raw_response, re.DOTALL)

    # def safe_extract(regex_match):
    #     try:
    #         return regex_match.group(1).strip()
    #     except:
    #         return ""
    def safe_extract(regex_match, group_num=1):
        try:
            return regex_match.group(group_num).strip()
        except:
            return ""
    
    print("🧪 Raw regex matches:")
    print("  cohrence_feedback:", bool(coherence_feedback))
    print("  lexical_feedback:", bool(lexical_feedback))
    print("  grammar_feedback:", bool(grammar_feedback))
    print("  overall_summary_feedback:", bool(overall_summary_feedback))
    print("  general_feedback:", bool(general_feedback))
    print("📥 Matched Task Feedback:", task_response_feedback.group(1) if task_response_feedback else "❌ Not found")
    print("📥 Matched Coherence Feedback:", coherence_feedback.group(1) if task_response_feedback else "❌ Not found")
    print("📥 Matched Lexical Feedback:", lexical_feedback.group(1) if task_response_feedback else "❌ Not found")
    print("📥 Matched Grammer Feedback:", grammar_feedback.group(1) if task_response_feedback else "❌ Not found")
    print("📥 Matched Overall Feedback:", overall_summary_feedback.group(1) if task_response_feedback else "❌ Not found")
    print("📥 Matched General Feedback:", general_feedback.group(1) if general_feedback else "❌ Not found")


    # Format the JSON response
    formatted_json = {
        "bands": {
            "task_response": int(task_response_score.group(1)) if task_response_score else None,
            "coherence_cohesion": int(coherence_score.group(1)) if coherence_score else None,
            "lexical_resource": int(lexical_score.group(1)) if lexical_score else None,
            "grammatical_range": int(grammar_score.group(1)) if grammar_score else None,
            "overall": int(overall_score.group(1)) if overall_score else None
        },
        # "feedback": {
        #     "task_response": task_response_feedback.group(1).strip() if task_response_feedback else "",
        #     "coherence_cohesion": coherence_feedback.group(1).strip() if coherence_feedback else "",
        #     "lexical_resource": lexical_feedback.group(1).strip() if lexical_feedback else "",
        #     "grammatical_range": grammar_feedback.group(1).strip() if grammar_feedback else "",
        #     "overall_summary": overall_summary_feedback.group(1).strip() if overall_summary_feedback else "",
        #     "general_feedback": general_feedback.group(1).strip() if general_feedback else ""
        # },
        "feedback": {
            "task_response": safe_extract(task_response_feedback,group_num=2),
            "coherence_cohesion": safe_extract(coherence_feedback),
            "lexical_resource": safe_extract(lexical_feedback),
            "grammatical_range": safe_extract(grammar_feedback),
            "overall_summary": safe_extract(overall_summary_feedback),
            "general_feedback": safe_extract(general_feedback)
        },
        "score_table": build_score_table({
            "task_response": task_response_score.group(1) if task_response_score else None,
            "coherence_cohesion": coherence_score.group(1) if coherence_score else None,
            "lexical_resource": lexical_score.group(1) if lexical_score else None,
            "grammatical_range": grammar_score.group(1) if grammar_score else None,
            "overall": overall_score.group(1) if overall_score else None
        })
    }
    print("🧪 Feedback Values:")
    for k, v in formatted_json["feedback"].items():
        print(f"{k}: {v[:100]}{'...' if len(v) > 100 else ''}")
    
    print("🧪 Parsed scores:", {
        "task": task_response_score.group(1) if task_response_score else None,
        "coherence": coherence_score.group(1) if coherence_score else None,
        "lexical": lexical_score.group(1) if lexical_score else None,
        "grammar": grammar_score.group(1) if grammar_score else None,
        "overall": overall_score.group(1) if overall_score else None
    })
    return formatted_json
