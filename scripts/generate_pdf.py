"""Generate corpus/medical_exemption.pdf with readable rulebook text."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fpdf import FPDF


PDF_BODY = """
Section 8.1 Purpose of Medical Exemption
Nexus University recognises that serious illness or injury may prevent a student from meeting ordinary academic attendance expectations. These Medical Exemption Rules apply for Academic Year 2026-2027. An exemption is not automatic. The student must apply, attach supporting evidence, and wait for written approval from the Medical Review Committee acting with the Office of the Registrar.

Section 8.2 Eligible Medical Circumstances
Eligible circumstances include hospitalisation of more than forty-eight hours, communicable disease requiring isolation on medical advice, scheduled surgery with a recovery period certified by a registered medical practitioner, and acute psychiatric crisis treated by the University Health Centre or an equivalent licensed facility. Seasonal cold, routine outpatient visits, and undocumented fatigue are not eligible. Travel for rest is not a medical ground.

Section 8.3 Application Procedure
The student shall submit Form MX-26 within seven calendar days of returning to academic activity, or earlier if the absence is foreseeable. The form must include diagnosis category, period of incapacity, treating practitioner registration number, and a statement of academic impact. Delayed applications may be accepted only where the student was medically incapable of filing on time, as certified in writing.

Section 8.4 Examination Eligibility After Approved Medical Exemption
Where a student has received an approved medical exemption covering the relevant teaching period, the student may be permitted to appear for the semester examination if the student has maintained at least 60% attendance in that course, counted after excluding days covered by the approved exemption. This medical pathway is intended to prevent unfair exclusion of students who were hospitalised or otherwise certified unfit. Coursework still due must be completed under a make-up schedule issued by the course instructor and recorded by the Department Office.

Section 8.5 Supporting Documents and Verification
The University may verify certificates with the issuing hospital or clinic. Forged, altered, or purchased medical documents constitute academic misconduct under the Student Discipline Code and may lead to cancellation of the exemption, failure in the course, and disciplinary probation. Students must keep original documents for one year after the decision.

Section 8.6 Limits of Exemption
A medical exemption does not waive tuition, hostel rent, or examination fees. It does not authorise absence from a university inquiry, does not extend the maximum duration of the programme, and does not create a right to a special examination date except as separately provided in the Examination Rules. Repeat medical exemptions in consecutive semesters are reviewed with heightened scrutiny.

Section 8.7 Notification to Departments
After approval, the Registrar shall notify the Head of Department, the course instructors concerned, and the Controller of Examinations. Instructors shall not reduce internal assessment solely because medically exempted hours were missed, provided the student completes an equivalent academic task when reasonably possible.

Section 8.8 Appeals
A student may appeal a refused medical exemption to the Dean of Student Affairs within ten working days. The appeal board shall include one faculty member from outside the student's department and one medical adviser who was not the original reviewer. The appeal decision is final for that semester.
""".strip()


class RulePdf(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, "Nexus University  |  Academic Year 2026-2027", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 6, "Medical Exemption Rules  (Office of the Registrar)", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def generate_pdf(output: Path | None = None) -> Path:
    path = output or (ROOT / "corpus" / "medical_exemption.pdf")
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = RulePdf()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 11)
    for block in PDF_BODY.split("\n\n"):
        pdf.multi_cell(0, 6, block.strip())
        pdf.ln(3)
    pdf.output(str(path))
    return path


if __name__ == "__main__":
    written = generate_pdf()
    print(f"Wrote {written}")
