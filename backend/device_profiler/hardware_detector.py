"""
Hardware Detector module for GreenMind.
Inspects CPU, RAM, GPU/Accelerators, and Battery/Power state across Windows, Linux, and macOS.
"""

import csv
import io
import platform
import subprocess
from typing import Dict, Any, List

import psutil



class HardwareDetector:
    """Detects and telemeters hardware resources and live operating states."""


    def __init__(self):

        self.os_name = platform.system()



    def get_complete_telemetry(self) -> Dict[str, Any]:

        return {

            "system": self._get_os_info(),

            "cpu": self._get_cpu_info(),

            "memory": self._get_memory_info(),

            "gpu": self._get_gpu_info(),

            "power": self._get_power_info(),

        }




    def _get_os_info(self) -> Dict[str, Any]:

        return {

            "platform": self.os_name,

            "release": platform.release(),

            "version": platform.version(),

            "architecture": platform.machine(),

            "hostname": platform.node(),

        }





    def _get_cpu_info(self) -> Dict[str, Any]:
        """
        CPU model, core counts, clocks, and live utilization.
        """

        physical_cores = psutil.cpu_count(logical=False) or 1

        logical_cores = psutil.cpu_count(logical=True) or 1

        cpu_usage_pct = psutil.cpu_percent(interval=0.2)



        freq = psutil.cpu_freq()

        current_freq_mhz = (
            round(freq.current,1)
            if freq and freq.current
            else None
        )


        max_freq_mhz = (
            round(freq.max,1)
            if freq and freq.max
            else None
        )



        # ==========================
        # Improved CPU Detection
        # ==========================


        cpu_name = platform.processor() or platform.machine()



        # macOS detection

        if self.os_name == "Darwin":

            try:

                cpu_name = subprocess.check_output(

                    [
                        "sysctl",
                        "-n",
                        "machdep.cpu.brand_string"
                    ]

                ).decode().strip()


            except Exception:


                try:

                    cpu_name = subprocess.check_output(

                        [
                            "sysctl",
                            "-n",
                            "hw.model"
                        ]

                    ).decode().strip()


                except Exception:

                    cpu_name = platform.machine()



        # Windows detection

        elif self.os_name == "Windows":

            cpu_name = (
                self._get_windows_cpu_name()
                or cpu_name
            )



        return {


            "model": cpu_name,


            "physical_cores": physical_cores,


            "logical_threads": logical_cores,


            "current_frequency_mhz": current_freq_mhz,


            "max_frequency_mhz": max_freq_mhz,


            "utilization_pct": cpu_usage_pct,


        }







    def _get_windows_cpu_name(self) -> str:

        try:

            cmd = [

                "powershell",

                "-NoProfile",

                "-Command",

                "Get-CimInstance Win32_Processor | Select-Object Name | ConvertTo-Csv -NoTypeInformation"

            ]


            res = subprocess.run(

                cmd,

                capture_output=True,

                text=True,

                timeout=5

            )



            if res.returncode == 0:

                reader = csv.DictReader(
                    io.StringIO(
                        res.stdout.strip()
                    )
                )


                for row in reader:

                    name = row.get("Name")

                    if name:

                        return name.strip()


        except Exception:

            pass


        return ""







    def _get_memory_info(self) -> Dict[str, Any]:

        vm = psutil.virtual_memory()

        swap = psutil.swap_memory()



        return {


            "total_gb":

            round(vm.total/(1024**3),2),



            "available_gb":

            round(vm.available/(1024**3),2),



            "used_gb":

            round(vm.used/(1024**3),2),



            "utilization_pct":

            vm.percent,



            "swap_total_gb":

            round(swap.total/(1024**3),2),



            "swap_used_gb":

            round(swap.used/(1024**3),2),


        }







    def _get_gpu_info(self) -> List[Dict[str, Any]]:


        gpus=[]


        if self.os_name=="Windows":

            gpus=self._get_windows_gpus()


        elif self.os_name=="Linux":

            gpus=self._get_linux_gpus()



        if not gpus:

            gpus.append({

                "name":
                "Integrated / Software Render",

                "dedicated_vram_gb":
                0.0,

                "type":
                "Integrated"

            })


        return gpus







    def _get_windows_gpus(self):

        gpus=[]


        try:

            cmd=[

                "powershell",

                "-NoProfile",

                "-Command",

                "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM | ConvertTo-Csv -NoTypeInformation"

            ]


            res=subprocess.run(

                cmd,

                capture_output=True,

                text=True,

                timeout=5

            )


            if res.returncode==0:


                reader=csv.DictReader(

                    io.StringIO(
                        res.stdout.strip()
                    )

                )


                for row in reader:


                    name=row.get("Name","").strip()


                    if name:


                        gpus.append({

                            "name":name,

                            "dedicated_vram_gb":0,

                            "type":"Integrated"

                        })


        except Exception:

            pass



        return gpus








    def _get_linux_gpus(self):

        return []







    def _get_power_info(self):

        battery=psutil.sensors_battery()



        if battery is None:

            return {

                "has_battery":False,

                "power_plugged":True,

                "percent":100,

                "status":"AC Desktop"

            }



        return {


            "has_battery":True,


            "power_plugged":
            bool(battery.power_plugged),


            "percent":
            int(battery.percent),


            "status":
            "Plugged In (AC)"
            if battery.power_plugged
            else
            "On Battery (Discharging)"

        }