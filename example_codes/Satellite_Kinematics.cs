using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using Microsoft.VisualBasic;
using Microsoft.VisualBasic.CompilerServices;
using Zeptomoby.OrbitTools;

namespace Command_Core
{
    public sealed class Satellite_Kinematics : ActiveUnit_Kinematics
	{
		private Zeptomoby.OrbitTools.Satellite _satellite;

		private Satellite_Orbit.Ephemeris _ephemeris;

		public Satellite_Kinematics(ref ActiveUnit activeUnit_1)
			: base(ref activeUnit_1)
		{
		}

		[SpecialName]
		public long GetApogee()
		{
			if (Information.IsNothing(_ephemeris))
			{
				return (long)Math.Round(_satellite.Orbit.ApogeeKmRec * 1000.0);
			}
			return (long)Math.Round(_ephemeris.GetApogee() * 1000.0);
		}

		[SpecialName]
		public long GetPerigee()
		{
			if (Information.IsNothing(_ephemeris))
			{
				return (long)Math.Round(_satellite.Orbit.PerigeeKmRec * 1000.0);
			}
			return (long)Math.Round(_ephemeris.GetPerigee() * 1000.0);
		}

		public void LoadOrbitalElements(float float_5, long long_0, long long_1)
		{
			_satellite = null;
			_ephemeris = new Satellite_Orbit.Ephemeris();
			_ephemeris.ReInit(float_5, (double)long_0 / 1000.0, (double)long_1 / 1000.0);
			Move(0f, bool_3: false, bool_4: false, ParentPlatform.m_Scenario.GetCurrentTime());
		}

		public void LoadTleData(string[] string_1)
		{
			_ephemeris = null;
			if (string_1.Length == 2)
			{
				List<string> list = string_1.ToList();
				list.Insert(0, "Mysat");
				string_1 = list.ToArray();
			}
			TwoLineElements tle = new TwoLineElements(string_1[0], string_1[1], string_1[2]);
			_satellite = new Zeptomoby.OrbitTools.Satellite(tle);
			Move(0f, bool_3: false, bool_4: false, ParentPlatform.m_Scenario.GetCurrentTime());
		}

		public void CalculateOrbit(DateTime dateTime, ref double latitude, ref double longitude, ref double altitude, ref double horizontalSpeed)
		{
			Command_Core.Satellite.SatelliteOrbitAnchor geo = ((Command_Core.Satellite)ParentPlatform).OrbitAnchor;
			if (geo != null)
			{
				longitude = geo.LongitudeDeg;
				latitude = geo.LatitudeDeg;
				altitude = geo.Altitude / 1000f;
				horizontalSpeed = 0.0;
				return;
			}
			if (_ephemeris == null)
			{
				EciTime eciTime = _satellite.PositionEci(dateTime.ToUniversalTime());
				Geo geo2 = new Geo(eciTime, new Julian(dateTime.ToUniversalTime()));
				latitude = geo2.LatitudeDeg;
				longitude = geo2.LongitudeDeg;
				altitude = geo2.Altitude;
				double num = Math.Abs(eciTime.Velocity.X * 1000.0);
				horizontalSpeed = num * 1.94384;
				return;
			}
			double speed = default(double);
			_ephemeris.Predict_Position(dateTime, bool_0: true, ref latitude, ref longitude, ref altitude, ref speed);
			if (altitude < (double)GetPerigee() / 1000.0)
			{
				altitude = (double)GetPerigee() / 1000.0;
			}
			if (altitude > (double)GetApogee() / 1000.0)
			{
				altitude = (double)GetApogee() / 1000.0;
			}
			horizontalSpeed = speed * 1000.0 * 1.94384;
		}

		public override void Move(float float_5, bool bool_3, bool bool_4, DateTime dateTime_0)
		{
			try
			{
				double double_ = default(double);
				double double_2 = default(double);
				double double_3 = default(double);
				double double_4 = default(double);
				CalculateOrbit(dateTime_0, ref double_, ref double_2, ref double_3, ref double_4);
				double double_5 = default(double);
				double double_6 = default(double);
				double double_7 = default(double);
				double double_8 = default(double);
				CalculateOrbit(dateTime_0.AddSeconds(1.0), ref double_5, ref double_6, ref double_7, ref double_8);
				ParentPlatform.SetCurrentHeading(Math2.CalcAzimuth(double_, double_2, double_5, double_6));
				if (ParentPlatform.m_Scenario.GetTimeCompression_SimSeconds() > 1)
				{
					ParentPlatform.SetLatitude(null, double_);
					ParentPlatform.SetLongitude(null, double_2);
					ParentPlatform.SetCurrentAltitude(DoSanityCheck: false, (float)(double_3 * 1000.0));
					ParentPlatform.SetCurrentSpeed((float)double_4);
				}
				else
				{
					float num = (float)((double)dateTime_0.Millisecond / 1000.0);
					float num2 = Math2.CalcDist(double_, double_2, double_5, double_6);
					float num3 = num * num2;
					ActiveUnit activeUnit;
					ActiveUnit activeUnit2 = (activeUnit = ParentPlatform);
					bool? hintIsOperating = null;
					double double_9 = activeUnit2.GetLongitude(hintIsOperating);
					ActiveUnit activeUnit3;
					ActiveUnit activeUnit4 = (activeUnit3 = ParentPlatform);
					bool? hintIsOperating2 = null;
					double double_10 = activeUnit4.GetLatitude(hintIsOperating2);
					ActiveUnit activeUnit5;
					float float_6 = (activeUnit5 = ParentPlatform).GetCurrentHeading();
					Geodesic_EdWilliams.CalcPoint_Williams(ref double_2, ref double_, ref double_9, ref double_10, ref num3, ref float_6);
					activeUnit5.SetCurrentHeading(float_6);
					activeUnit3.SetLatitude(hintIsOperating2, double_10);
					activeUnit.SetLongitude(hintIsOperating, double_9);
					ParentPlatform.SetCurrentAltitude(DoSanityCheck: false, (float)((double_3 + (double_7 - double_3) * (double)num) * 1000.0));
					ParentPlatform.SetCurrentSpeed((float)(double_4 + (double_8 - double_4) * (double)num));
				}
				ParentPlatform.SetLongitudeLR(ParentPlatform.GetLongitude());
				ParentPlatform.SetLatitudeLR(ParentPlatform.GetLatitude());
				ParentPlatform.GetKinematics().ExportUnitPositions(forceUpdate: false);
			}
			catch (Exception ex)
			{
				ProjectData.SetProjectError(ex);
				Exception exception_ = ex;
				exception_.Data.Add("Error at 100755", "");
				GameGeneral.LogException(ref exception_);
				if (Debugger.IsAttached)
				{
					Debugger.Break();
				}
				ProjectData.ClearProjectError();
			}
		}

	}
}
